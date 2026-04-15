"""
dump_transcripts.py -- conv_trials.jsonl から (model, persona) ごとに
C0/C1/C2 3 条件の timing 比較つきトランスクリプトを生成する。

temp=0 seed=42 なので返答テキストは 3 条件で同一。違うのは timing だけで、
それこそが実験の本題なので 3 条件を並べて見せる。
"""

import json
import os
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TRIALS = os.path.join(ROOT, "results", "raw", "conv_trials.jsonl")
OUT_DIR = os.path.join(ROOT, "results", "summary", "transcripts")
os.makedirs(OUT_DIR, exist_ok=True)

MODEL_LABEL = {
    "M3B": "Qwen2.5-3B-Instruct",
    "M7B": "Qwen2.5-7B-Instruct",
    "M14B": "Qwen2.5-14B-Instruct",
    "M30A3": "Qwen3-30B-A3B",
    "M32B": "Qwen2.5-32B-Instruct",
    "M72B": "Qwen2.5-72B-Instruct",
}
PERSONA_LABEL = {
    "P0": "汎用アシスタント",
    "P1": "RPG NPC 薬草商人リナ (/no_think)",
    "P2": "引退漁師 富田源次郎",
}
COND_LABEL = {
    "C0": "C0 baseline (no cache)",
    "C1": "C1 cache_prompt",
    "C2": "C2 cache_prompt + spec",
}
CONDS = ["C0", "C1", "C2"]

# dedupe: failed runs leave partial trials before a later full run appends.
# keep the LAST appearance of each (case_id, turn).
latest = {}
with open(TRIALS, encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        t = json.loads(line)
        latest[(t["case_id"], t["turn"])] = t

by_mpc = defaultdict(dict)
for t in latest.values():
    _, mk, pk, ck = t["case_id"].split("-")
    by_mpc[(mk, pk, ck)][t["turn"]] = t

pairs = sorted({(mk, pk) for (mk, pk, _) in by_mpc.keys()})


def fmt_spec(r):
    dn = r.get("draft_n") or 0
    da = r.get("draft_accepted") or 0
    if not dn:
        return "—"
    return f"{da}/{dn} ({100 * da / dn:.0f}%)"


def fmt_sec(x):
    if x is None:
        return "—"
    return f"{x:.1f}s"


for mk, pk in pairs:
    model = MODEL_LABEL.get(mk, mk)
    persona = PERSONA_LABEL.get(pk, pk)

    conds = {}
    for ck in CONDS:
        if (mk, pk, ck) in by_mpc:
            conds[ck] = by_mpc[(mk, pk, ck)]
    if not conds:
        continue

    turn_numbers = sorted(next(iter(conds.values())).keys())

    lines = [f"# {model} × {persona}", ""]
    lines.append(
        "temp=0, seed=42 の決定論セッティングなので C0/C1/C2 の返答テキストは同一。"
        "違うのは速度だけ。下のサマリと各ターン表がその比較。"
    )
    lines.append("")

    # 全体サマリ
    lines.append("## 20 ターン合計")
    lines.append("")
    lines.append(
        "| cond | total elapsed | prefill total | gen total | prompt tok合計 | gen tok合計 | 平均 prefill tps | 平均 gen tps | spec 受理 |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    baseline_total = None
    for ck in CONDS:
        if ck not in conds:
            continue
        rs = [conds[ck][tn] for tn in turn_numbers if tn in conds[ck]]
        total_e = sum(r.get("elapsed_sec") or 0 for r in rs)
        total_pre = sum((r.get("prompt_ms") or 0) / 1000 for r in rs)
        total_gen = sum((r.get("predict_ms") or 0) / 1000 for r in rs)
        total_p = sum(r.get("prompt_tokens") or 0 for r in rs)
        total_g = sum(r.get("gen_tokens") or 0 for r in rs)
        avg_p_tps = sum(r.get("prompt_tps") or 0 for r in rs) / len(rs)
        avg_g_tps = sum(r.get("gen_tps") or 0 for r in rs) / len(rs)
        dn = sum(r.get("draft_n") or 0 for r in rs)
        da = sum(r.get("draft_accepted") or 0 for r in rs)
        spec = f"{da}/{dn} ({100 * da / dn:.0f}%)" if dn else "—"
        if ck == "C0":
            baseline_total = total_e
        lines.append(
            f"| {COND_LABEL[ck]} | {total_e:.1f}s | {total_pre:.1f}s | {total_gen:.1f}s "
            f"| {total_p} | {total_g} | {avg_p_tps:.1f} | {avg_g_tps:.1f} | {spec} |"
        )

    if baseline_total and "C2" in conds:
        c2_total = sum(conds["C2"][tn]["elapsed_sec"] for tn in turn_numbers if tn in conds["C2"])
        if c2_total:
            lines.append("")
            lines.append(
                f"**C2/C0 speedup: {baseline_total / c2_total:.2f}x**  "
                f"({baseline_total:.0f}s → {c2_total:.0f}s)"
            )
    if baseline_total and "C1" in conds:
        c1_total = sum(conds["C1"][tn]["elapsed_sec"] for tn in turn_numbers if tn in conds["C1"])
        if c1_total:
            lines.append("")
            lines.append(
                f"**C1/C0 speedup: {baseline_total / c1_total:.2f}x**  "
                f"({baseline_total:.0f}s → {c1_total:.0f}s)"
            )
    lines.append("")
    lines.append("---")
    lines.append("")

    # 各ターン
    for tn in turn_numbers:
        base = conds.get("C0", {}).get(tn) or next(
            (conds[ck][tn] for ck in CONDS if ck in conds and tn in conds[ck]), None
        )
        if base is None:
            continue
        prompt_tok = base.get("prompt_tokens") or 0
        gen_tok = base.get("gen_tokens") or 0

        lines.append(f"## Turn {tn}")
        lines.append("")
        lines.append(f"_prompt {prompt_tok} tok → gen {gen_tok} tok_")
        lines.append("")

        # 3 条件 timing 比較
        lines.append("| cond | elapsed | prefill | gen | spec accept |")
        lines.append("|---|---:|---:|---:|---:|")
        for ck in CONDS:
            if ck not in conds or tn not in conds[ck]:
                continue
            r = conds[ck][tn]
            el = r.get("elapsed_sec") or 0
            p_ms = r.get("prompt_ms") or 0
            p_tps = r.get("prompt_tps") or 0
            g_ms = r.get("predict_ms") or 0
            g_tps = r.get("gen_tps") or 0
            spec = fmt_spec(r) if ck == "C2" else "—"
            lines.append(
                f"| {ck} | {el:.1f}s | {p_ms / 1000:.2f}s @ {p_tps:.0f} tps "
                f"| {g_ms / 1000:.1f}s @ {g_tps:.1f} tps | {spec} |"
            )
        lines.append("")

        lines.append(f"**User**: {base['user']}")
        lines.append("")
        assistant = (base.get("assistant") or "").strip()
        lines.append("**Assistant**:")
        lines.append("")
        for ln in assistant.splitlines():
            lines.append(f"> {ln}" if ln else ">")
        lines.append("")

    out_path = os.path.join(OUT_DIR, f"{mk}_{pk}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {out_path}")
