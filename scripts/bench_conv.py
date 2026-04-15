"""
bench_conv.py -- E6 会話ベンチ (llama.cpp 推論側最適化の効き方を多軸で測る)

マトリクス:
  モデル   6: Qwen2.5 {3B, 7B, 14B, 32B, 72B} / Qwen3-30B-A3B (全 Q4_K_M)
  ペルソナ 3: P0 汎用アシスタント / P1 RPG NPC 薬草商人リナ / P2 引退漁師 富田源次郎
  条件     3: C0 baseline (--no-cache-prompt) / C1 cache_prompt / C2 cache + speculative decoding
  ターン   20 (persona ごとに対応する質問セットを固定)

  → 6 × 3 × 3 = 54 ラン × 20 ターン = 1080 ターン

保存:
  results/raw/conv.csv                 -- ラン単位集計
  results/raw/conv_trials.jsonl        -- ターン単位 (user/assistant 全文 + timings)
  results/raw/responses/<case>/NN.json -- /v1/chat/completions の生レスポンス
  results/raw/logs/<case>.log          -- llama-server stdout+stderr
  results/raw/configs/<case>.json      -- 起動コマンドと設定スナップショット

resume:
  既に conv.csv に書かれた case_id はスキップ。途中落ちしても同じコマンドで再開可。

Usage:
  python bench_conv.py
  python bench_conv.py --only M3B M7B            # 特定モデルだけ
  python bench_conv.py --skip M72B                # 特定モデルを外す
"""

import argparse
import csv
import json
import os
import shlex
import subprocess
import sys
import time
import urllib.request
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

BASE_DIR = r"C:\llm-exp"
LLAMA_SERVER = os.path.join(BASE_DIR, "llama.cpp", "llama-server.exe")
MODELS_DIR = os.path.join(BASE_DIR, "models")
RAW_DIR = os.path.join(BASE_DIR, "results", "raw")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(os.path.join(RAW_DIR, "responses"), exist_ok=True)
os.makedirs(os.path.join(RAW_DIR, "logs"), exist_ok=True)
os.makedirs(os.path.join(RAW_DIR, "configs"), exist_ok=True)

CONV_CSV = os.path.join(RAW_DIR, "conv.csv")
CONV_JSONL = os.path.join(RAW_DIR, "conv_trials.jsonl")

PORT = 8080
CONTEXT = 8192
MAX_TOKENS_PER_TURN = 1024

# --------------------------------------------------------------------------
# モデル
# --------------------------------------------------------------------------
MODELS = [
    {
        "key": "M3B",
        "file": "Qwen2.5-3B-Instruct-Q4_K_M.gguf",
        "family": "qwen2.5",
        "draft": "Qwen2.5-0.5B-Instruct-Q8_0.gguf",
        "label": "Qwen2.5-3B",
    },
    {
        "key": "M7B",
        "file": "Qwen2.5-7B-Instruct-Q4_K_M.gguf",
        "family": "qwen2.5",
        "draft": "Qwen2.5-0.5B-Instruct-Q8_0.gguf",
        "label": "Qwen2.5-7B",
    },
    {
        "key": "M14B",
        "file": "Qwen2.5-14B-Instruct-Q4_K_M.gguf",
        "family": "qwen2.5",
        "draft": "Qwen2.5-0.5B-Instruct-Q8_0.gguf",
        "label": "Qwen2.5-14B",
    },
    {
        "key": "M30A3",
        "file": "Qwen3-30B-A3B-Q4_K_M.gguf",
        "family": "qwen3",
        "draft": "Qwen3-0.6B-Q8_0.gguf",
        "label": "Qwen3-30B-A3B",
    },
    {
        "key": "M32B",
        "file": "Qwen2.5-32B-Instruct-Q4_K_M.gguf",
        "family": "qwen2.5",
        "draft": "Qwen2.5-0.5B-Instruct-Q8_0.gguf",
        "label": "Qwen2.5-32B",
    },
    {
        "key": "M72B",
        "file": "Qwen2.5-72B-Instruct-Q4_K_M.gguf",
        "family": "qwen2.5",
        "draft": "Qwen2.5-0.5B-Instruct-Q8_0.gguf",
        "label": "Qwen2.5-72B",
        "ngl": 18,
        "ctx": 6144,
    },
]

# --------------------------------------------------------------------------
# ペルソナ / 質問セット
#   P1 (RPG) のみ /no_think、P0/P2 は thinking 許容
#   Qwen2.5 系は /no_think を無視するので全系列で同じ system prompt が使える
# --------------------------------------------------------------------------
def load_text(name):
    path = os.path.join(RAW_DIR, "prompts", name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().rstrip()


def load_json(name):
    path = os.path.join(RAW_DIR, "prompts", name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


PERSONAS = [
    {
        "key": "P0",
        "label": "plain-assistant",
        "system": load_text("persona_p0.txt"),
        "questions": load_json("questions_q0.json")["turns"],
        "thinking": "allow",
    },
    {
        "key": "P1",
        "label": "rpg-rina",
        "system": load_text("persona_p1.txt"),
        "questions": load_json("questions_q1.json")["turns"],
        "thinking": "disable",
    },
    {
        "key": "P2",
        "label": "retired-fisher",
        "system": load_text("persona_p2.txt"),
        "questions": load_json("questions_q2.json")["turns"],
        "thinking": "allow",
    },
]

CONDITIONS = [
    {"key": "C0", "label": "baseline", "cache_prompt": False, "speculative": False},
    {"key": "C1", "label": "cache", "cache_prompt": True, "speculative": False},
    {"key": "C2", "label": "cache+spec", "cache_prompt": True, "speculative": True},
]


# --------------------------------------------------------------------------
# llama-server 起動 / 停止
# --------------------------------------------------------------------------
def build_server_cmd(model, cond):
    ngl = str(model.get("ngl", 999))
    ctx = str(model.get("ctx", CONTEXT))
    cmd = [
        LLAMA_SERVER,
        "-m", os.path.join(MODELS_DIR, model["file"]),
        "-ngl", ngl,
        "-c", ctx,
        "-fa", "on",
        "--host", "127.0.0.1",
        "--port", str(PORT),
        "--threads", "16",
        "--seed", "42",
    ]
    if not cond["cache_prompt"]:
        cmd += ["--no-cache-prompt"]
    if cond["speculative"]:
        cmd += [
            "-md", os.path.join(MODELS_DIR, model["draft"]),
            "-ngld", "999",
            "--draft-max", "8",
            "--draft-min", "1",
        ]
    return cmd


def kill_stale_servers():
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "llama-server.exe"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def start_server(cmd, log_path):
    kill_stale_servers()
    time.sleep(2)
    print(f"  Starting: {' '.join(shlex.quote(x) for x in cmd)}")
    log_f = open(log_path, "wb")
    proc = subprocess.Popen(cmd, stdout=log_f, stderr=subprocess.STDOUT)
    t0 = time.perf_counter()
    for _ in range(240):  # 最長 8 分、72B のロード余裕込み
        time.sleep(2)
        if proc.poll() is not None:
            log_f.close()
            return None, 0.0, log_f
        try:
            urllib.request.urlopen(f"http://localhost:{PORT}/health", timeout=2)
            load_sec = time.perf_counter() - t0
            print(f"  Ready ({load_sec:.1f}s)")
            return proc, load_sec, log_f
        except Exception:
            pass
    proc.kill()
    log_f.close()
    return None, 0.0, log_f


def stop_server(proc, log_f):
    if proc:
        proc.kill()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            pass
    if log_f:
        try:
            log_f.close()
        except Exception:
            pass
    kill_stale_servers()
    time.sleep(4)


# --------------------------------------------------------------------------
# /v1/chat/completions 呼び出し
# --------------------------------------------------------------------------
def chat_turn(messages):
    body = {
        "model": "x",
        "messages": messages,
        "temperature": 0.0,
        "top_k": 40,
        "top_p": 0.95,
        "seed": 42,
        "max_tokens": MAX_TOKENS_PER_TURN,
        "stream": False,
    }
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    last_err = None
    t0 = time.perf_counter()
    for attempt in range(3):
        req = urllib.request.Request(
            f"http://localhost:{PORT}/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            raw = urllib.request.urlopen(req, timeout=1800).read()
            elapsed = time.perf_counter() - t0
            return json.loads(raw), raw, elapsed
        except (ConnectionResetError, ConnectionAbortedError, TimeoutError) as e:
            last_err = e
            print(f"    chat_turn retry {attempt+1}/3 after {type(e).__name__}: {str(e)[:80]}")
            time.sleep(3 + attempt * 5)
    raise last_err


# --------------------------------------------------------------------------
# 1 ラン実行
# --------------------------------------------------------------------------
def run_case(model, persona, cond):
    case_id = f"E6-{model['key']}-{persona['key']}-{cond['key']}"
    print(f"\n{'='*78}\n  CASE: {case_id}  ({model['label']} / {persona['label']} / {cond['label']})\n{'='*78}")

    log_path = os.path.join(RAW_DIR, "logs", f"{case_id}.log")
    cfg_path = os.path.join(RAW_DIR, "configs", f"{case_id}.json")
    resp_dir = os.path.join(RAW_DIR, "responses", case_id)
    os.makedirs(resp_dir, exist_ok=True)

    cmd = build_server_cmd(model, cond)
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump({
            "case_id": case_id,
            "date": datetime.now().isoformat(timespec="seconds"),
            "model": model,
            "persona": {k: v for k, v in persona.items() if k != "system" and k != "questions"},
            "cond": cond,
            "context": int(model.get("ctx", CONTEXT)),
            "max_tokens_per_turn": MAX_TOKENS_PER_TURN,
            "server_cmd": cmd,
        }, f, ensure_ascii=False, indent=2)

    proc, load_sec, log_f = start_server(cmd, log_path)
    if proc is None:
        print(f"  server_failed_to_start -- see {log_path}")
        return {
            "case_id": case_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "model_key": model["key"], "model_file": model["file"], "model_family": model["family"],
            "persona_key": persona["key"], "persona_label": persona["label"],
            "cond_key": cond["key"], "cond_label": cond["label"],
            "backend": "vulkan+fa", "context": int(model.get("ctx", CONTEXT)),
            "cache_prompt": str(cond["cache_prompt"]).lower(),
            "speculative": str(cond["speculative"]).lower(),
            "turns": 0, "load_sec": 0, "total_elapsed_sec": 0,
            "avg_prompt_tps": 0, "avg_gen_tps": 0,
            "sum_prompt_tokens": 0, "sum_gen_tokens": 0,
            "stable": "false", "notes": "server_failed_to_start",
        }

    messages = [{"role": "system", "content": persona["system"]}]
    sum_prompt_tokens = 0
    sum_gen_tokens = 0
    sum_prompt_ms = 0.0
    sum_predict_ms = 0.0
    sum_elapsed = 0.0
    stable = True
    notes = "ok"

    try:
        for i, user_msg in enumerate(persona["questions"], 1):
            messages.append({"role": "user", "content": user_msg})
            try:
                resp, raw, elapsed = chat_turn(messages)
            except Exception as e:
                stable = False
                notes = f"turn_{i}_error: {type(e).__name__}: {str(e)[:120]}"
                print(f"  turn {i:2d}: ERROR {notes}")
                break
            with open(os.path.join(resp_dir, f"{i:02d}.json"), "wb") as f:
                f.write(raw)
            content = resp["choices"][0]["message"]["content"]
            content_clean = content.strip().replace("\ufffd", "")
            messages.append({"role": "assistant", "content": content_clean})
            usage = resp.get("usage", {})
            timings = resp.get("timings", {})
            prompt_tok = usage.get("prompt_tokens", timings.get("prompt_n", 0)) or 0
            gen_tok = usage.get("completion_tokens", timings.get("predicted_n", 0)) or 0
            prompt_ms = timings.get("prompt_ms", 0) or 0
            predict_ms = timings.get("predicted_ms", 0) or 0
            pp = timings.get("prompt_per_second", 0) or 0
            gp = timings.get("predicted_per_second", 0) or 0
            draft_n = timings.get("draft_n") if cond["speculative"] else None
            draft_accepted = timings.get("draft_n_accepted") if cond["speculative"] else None
            sum_prompt_tokens += prompt_tok
            sum_gen_tokens += gen_tok
            sum_prompt_ms += prompt_ms
            sum_predict_ms += predict_ms
            sum_elapsed += elapsed
            rec = {
                "case_id": case_id,
                "model_key": model["key"],
                "persona_key": persona["key"],
                "cond_key": cond["key"],
                "turn": i,
                "user": user_msg,
                "assistant": content.strip(),
                "elapsed_sec": round(elapsed, 3),
                "prompt_tokens": prompt_tok,
                "gen_tokens": gen_tok,
                "prompt_ms": round(prompt_ms, 1),
                "predict_ms": round(predict_ms, 1),
                "prompt_tps": round(pp, 1),
                "gen_tps": round(gp, 1),
                "draft_n": draft_n,
                "draft_accepted": draft_accepted,
            }
            with open(CONV_JSONL, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            extra = ""
            if cond["speculative"] and draft_n:
                acc = (draft_accepted / draft_n) if draft_n else 0
                extra = f" draft={draft_accepted}/{draft_n} ({acc*100:.0f}%)"
            print(f"  turn {i:2d}: p={prompt_tok:5d} g={gen_tok:4d} {elapsed:6.1f}s pp={pp:7.1f} gp={gp:5.1f}{extra}")
    finally:
        stop_server(proc, log_f)

    avg_prompt_tps = (sum_prompt_tokens / (sum_prompt_ms / 1000)) if sum_prompt_ms else 0
    avg_gen_tps = (sum_gen_tokens / (sum_predict_ms / 1000)) if sum_predict_ms else 0
    turns_done = (len(messages) - 1) // 2
    return {
        "case_id": case_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "model_key": model["key"], "model_file": model["file"], "model_family": model["family"],
        "persona_key": persona["key"], "persona_label": persona["label"],
        "cond_key": cond["key"], "cond_label": cond["label"],
        "backend": "vulkan+fa", "context": int(model.get("ctx", CONTEXT)),
        "cache_prompt": str(cond["cache_prompt"]).lower(),
        "speculative": str(cond["speculative"]).lower(),
        "turns": turns_done,
        "load_sec": round(load_sec, 1),
        "total_elapsed_sec": round(sum_elapsed, 2),
        "avg_prompt_tps": round(avg_prompt_tps, 1),
        "avg_gen_tps": round(avg_gen_tps, 1),
        "sum_prompt_tokens": sum_prompt_tokens,
        "sum_gen_tokens": sum_gen_tokens,
        "stable": "true" if stable else "false",
        "notes": notes,
    }


# --------------------------------------------------------------------------
# CSV / resume
# --------------------------------------------------------------------------
CSV_HEADERS = [
    "case_id", "date",
    "model_key", "model_file", "model_family",
    "persona_key", "persona_label",
    "cond_key", "cond_label",
    "backend", "context", "cache_prompt", "speculative",
    "turns", "load_sec", "total_elapsed_sec",
    "avg_prompt_tps", "avg_gen_tps",
    "sum_prompt_tokens", "sum_gen_tokens",
    "stable", "notes",
]


def load_done_case_ids():
    if not os.path.exists(CONV_CSV):
        return set()
    done = set()
    with open(CONV_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("stable") == "true" and int(row.get("turns") or 0) >= 1:
                done.add(row["case_id"])
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", default=None, help="run only these model keys")
    ap.add_argument("--skip", nargs="+", default=None, help="skip these model keys")
    args = ap.parse_args()

    active_models = [m for m in MODELS if (args.only is None or m["key"] in args.only) and (args.skip is None or m["key"] not in args.skip)]
    print(f"# models: {[m['key'] for m in active_models]}")
    print(f"# personas: {[p['key'] for p in PERSONAS]}")
    print(f"# conditions: {[c['key'] for c in CONDITIONS]}")
    total = len(active_models) * len(PERSONAS) * len(CONDITIONS)
    print(f"# total runs: {total}")

    done = load_done_case_ids()
    if done:
        print(f"# already done: {len(done)} cases (will skip)")

    write_header = not os.path.exists(CONV_CSV)
    with open(CONV_CSV, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if write_header:
            w.writeheader()
            f.flush()
        for model in active_models:
            for persona in PERSONAS:
                for cond in CONDITIONS:
                    case_id = f"E6-{model['key']}-{persona['key']}-{cond['key']}"
                    if case_id in done:
                        print(f"\n== skip {case_id} (already done)")
                        continue
                    t0 = time.perf_counter()
                    row = run_case(model, persona, cond)
                    dt = time.perf_counter() - t0
                    w.writerow({k: row.get(k, "") for k in CSV_HEADERS})
                    f.flush()
                    print(f"\n  SUMMARY {row['case_id']}: turns={row['turns']} total={row['total_elapsed_sec']}s avg_gen={row['avg_gen_tps']}tok/s stable={row['stable']} wall={dt:.1f}s")


if __name__ == "__main__":
    main()
