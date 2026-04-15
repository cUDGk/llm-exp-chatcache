"""
analyze.py -- E6 会話ベンチの集計・可視化

入力:
  results/raw/conv.csv
  results/raw/conv_trials.jsonl

出力:
  results/summary/summary.md
  results/summary/e6_total_p0.png
  results/summary/e6_total_p1.png
  results/summary/e6_total_p2.png
  results/summary/e6_speedup_heatmap.png
  results/summary/e6_prefill_heatmap.png
  results/summary/e6_turns_<model>_<persona>.png  (モデル×ペルソナごとの折れ線)
"""

import csv
import json
import os
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.family"] = ["Meiryo", "Yu Gothic", "MS Gothic", "Noto Sans JP", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(ROOT, "results", "raw")
OUT_DIR = os.path.join(ROOT, "results", "summary")
CONV_CSV = os.path.join(RAW_DIR, "conv.csv")
CONV_JSONL = os.path.join(RAW_DIR, "conv_trials.jsonl")
os.makedirs(OUT_DIR, exist_ok=True)

MODEL_ORDER = ["M3B", "M7B", "M14B", "M30A3", "M32B", "M72B"]
MODEL_LABEL = {
    "M3B": "Qwen2.5-3B",
    "M7B": "Qwen2.5-7B",
    "M14B": "Qwen2.5-14B",
    "M30A3": "Qwen3-30B-A3B",
    "M32B": "Qwen2.5-32B",
    "M72B": "Qwen2.5-72B",
}
PERSONA_ORDER = ["P0", "P1", "P2"]
PERSONA_LABEL = {
    "P0": "汎用アシスタント",
    "P1": "RPG NPC (薬草商人リナ)",
    "P2": "引退漁師 (富田源次郎)",
}
COND_ORDER = ["C0", "C1", "C2"]
COND_LABEL = {
    "C0": "baseline",
    "C1": "cache_prompt",
    "C2": "cache + spec",
}
COND_COLOR = {
    "C0": "#E45756",
    "C1": "#4C78A8",
    "C2": "#54A24B",
}


def load_cases():
    if not os.path.exists(CONV_CSV):
        return []
    with open(CONV_CSV, "r", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row.get("stable") == "true"]


def load_trials():
    if not os.path.exists(CONV_JSONL):
        return []
    out = []
    with open(CONV_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def f(c, key, default=0.0):
    try:
        return float(c[key])
    except (TypeError, ValueError, KeyError):
        return default


def index_cases(cases):
    # (model_key, persona_key, cond_key) -> row
    idx = {}
    for c in cases:
        idx[(c["model_key"], c["persona_key"], c["cond_key"])] = c
    return idx


def grouped_bar(persona_key, idx, out_path):
    models = [m for m in MODEL_ORDER if any((m, persona_key, ck) in idx for ck in COND_ORDER)]
    if not models:
        return
    fig, ax = plt.subplots(figsize=(10, 5.2))
    n_cond = len(COND_ORDER)
    width = 0.82 / n_cond
    xs = range(len(models))
    for i, ck in enumerate(COND_ORDER):
        values = []
        for m in models:
            row = idx.get((m, persona_key, ck))
            values.append(f(row, "total_elapsed_sec") if row else 0)
        offsets = [x + (i - (n_cond - 1) / 2) * width for x in xs]
        bars = ax.bar(offsets, values, width=width, label=COND_LABEL[ck], color=COND_COLOR[ck])
        for b, v in zip(bars, values):
            if v:
                ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.0f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([MODEL_LABEL[m] for m in models], rotation=0)
    ax.set_ylabel("total elapsed (s, 20 turns)")
    ax.set_title(f"E6: ペルソナ {PERSONA_LABEL[persona_key]} での 20 ターン総所要時間 (lower is better)")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def heatmap(idx, metric, title, out_path):
    # rows = model, cols = persona×(C1/C0, C2/C0)
    models = [m for m in MODEL_ORDER if any((m, p, c) in idx for p in PERSONA_ORDER for c in COND_ORDER)]
    cols = []
    for p in PERSONA_ORDER:
        cols.append((p, "C1"))
        cols.append((p, "C2"))
    data = []
    for m in models:
        row = []
        for p, ck in cols:
            base = idx.get((m, p, "C0"))
            target = idx.get((m, p, ck))
            if base and target:
                b = f(base, metric)
                t = f(target, metric)
                if metric == "total_elapsed_sec":
                    row.append(b / t if t else 0)  # speedup
                else:
                    row.append(t / b if b else 0)  # tps ratio
            else:
                row.append(float("nan"))
        data.append(row)

    fig, ax = plt.subplots(figsize=(9, 0.8 + 0.6 * len(models)))
    import numpy as np
    arr = np.array(data, dtype=float)
    im = ax.imshow(arr, aspect="auto", cmap="RdYlGn", vmin=0.8, vmax=max(2.0, np.nanmax(arr) if arr.size and not np.isnan(arr).all() else 2.0))
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([f"{p}/{ck}" for p, ck in cols], rotation=30, ha="right")
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([MODEL_LABEL[m] for m in models])
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            v = arr[i, j]
            if not (v != v):  # not NaN
                ax.text(j, i, f"{v:.2f}x", ha="center", va="center", fontsize=9, color="black")
    ax.set_title(title)
    fig.colorbar(im, ax=ax, fraction=0.035)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def per_turn_plots(trials):
    by_case = defaultdict(list)
    for t in trials:
        by_case[t["case_id"]].append(t)
    # group by (model, persona)
    groups = defaultdict(dict)  # (mk,pk) -> ck -> sorted turns
    for cid, rows in by_case.items():
        parts = cid.split("-")  # E6 M<x> P<y> C<z>
        if len(parts) != 4:
            continue
        _, mk, pk, ck = parts
        groups[(mk, pk)][ck] = sorted(rows, key=lambda r: r["turn"])
    for (mk, pk), condmap in groups.items():
        if not condmap:
            continue
        fig, ax = plt.subplots(figsize=(9, 4.5))
        for ck in COND_ORDER:
            rows = condmap.get(ck)
            if not rows:
                continue
            xs = [r["turn"] for r in rows]
            ys = [r["elapsed_sec"] for r in rows]
            ax.plot(xs, ys, marker="o", color=COND_COLOR[ck], label=COND_LABEL[ck])
        ax.set_xlabel("turn")
        ax.set_ylabel("elapsed (s)")
        ax.set_title(f"E6 turn-by-turn: {MODEL_LABEL.get(mk, mk)} / {PERSONA_LABEL.get(pk, pk)}")
        ax.set_xticks(range(1, 21))
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(OUT_DIR, f"e6_turns_{mk}_{pk}.png"), dpi=140)
        plt.close(fig)


def markdown_summary(cases, idx, trials):
    lines = []
    lines.append("# E6 会話ベンチ結果サマリ\n")
    lines.append(f"- 総ラン数: {len(cases)}")
    lines.append("")
    lines.append("## 1. マトリクス全体 (total elapsed / 20 ターン)\n")
    lines.append("| model | persona | C0 baseline | C1 cache | C2 cache+spec | C1/C0 | C2/C0 |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for m in MODEL_ORDER:
        for p in PERSONA_ORDER:
            c0 = idx.get((m, p, "C0"))
            c1 = idx.get((m, p, "C1"))
            c2 = idx.get((m, p, "C2"))
            if not any([c0, c1, c2]):
                continue
            v0 = f(c0, "total_elapsed_sec") if c0 else float("nan")
            v1 = f(c1, "total_elapsed_sec") if c1 else float("nan")
            v2 = f(c2, "total_elapsed_sec") if c2 else float("nan")
            r1 = (v0 / v1) if v1 else float("nan")
            r2 = (v0 / v2) if v2 else float("nan")
            lines.append(f"| {MODEL_LABEL.get(m, m)} | {p} | {v0:.1f} | {v1:.1f} | {v2:.1f} | {r1:.2f}x | {r2:.2f}x |")
    lines.append("")

    lines.append("## 2. prefill スループット (tok/s)\n")
    lines.append("| model | persona | C0 | C1 | C2 | C1/C0 | C2/C0 |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for m in MODEL_ORDER:
        for p in PERSONA_ORDER:
            c0 = idx.get((m, p, "C0"))
            c1 = idx.get((m, p, "C1"))
            c2 = idx.get((m, p, "C2"))
            if not any([c0, c1, c2]):
                continue
            p0 = f(c0, "avg_prompt_tps") if c0 else float("nan")
            p1 = f(c1, "avg_prompt_tps") if c1 else float("nan")
            p2 = f(c2, "avg_prompt_tps") if c2 else float("nan")
            r1 = (p1 / p0) if p0 else float("nan")
            r2 = (p2 / p0) if p0 else float("nan")
            lines.append(f"| {MODEL_LABEL.get(m, m)} | {p} | {p0:.0f} | {p1:.0f} | {p2:.0f} | {r1:.2f}x | {r2:.2f}x |")
    lines.append("")

    lines.append("## 3. gen スループット (tok/s)\n")
    lines.append("| model | persona | C0 | C1 | C2 | C2/C0 |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for m in MODEL_ORDER:
        for p in PERSONA_ORDER:
            c0 = idx.get((m, p, "C0"))
            c1 = idx.get((m, p, "C1"))
            c2 = idx.get((m, p, "C2"))
            if not any([c0, c1, c2]):
                continue
            g0 = f(c0, "avg_gen_tps") if c0 else float("nan")
            g1 = f(c1, "avg_gen_tps") if c1 else float("nan")
            g2 = f(c2, "avg_gen_tps") if c2 else float("nan")
            r2 = (g2 / g0) if g0 else float("nan")
            lines.append(f"| {MODEL_LABEL.get(m, m)} | {p} | {g0:.1f} | {g1:.1f} | {g2:.1f} | {r2:.2f}x |")
    lines.append("")

    # draft 受理率 (C2 ケースのみ)
    draft_rows = []
    for cid_key in idx:
        if cid_key[2] != "C2":
            continue
        mk, pk, _ = cid_key
        # aggregate from trials
        ns = [t.get("draft_n") for t in trials if t.get("case_id") == f"E6-{mk}-{pk}-C2" and t.get("draft_n") is not None]
        acs = [t.get("draft_accepted") for t in trials if t.get("case_id") == f"E6-{mk}-{pk}-C2" and t.get("draft_accepted") is not None]
        if ns and acs:
            total_n = sum(ns)
            total_ac = sum(acs)
            rate = (total_ac / total_n) if total_n else 0
            draft_rows.append((mk, pk, total_n, total_ac, rate))
    if draft_rows:
        lines.append("## 4. speculative decoding 受理率 (C2)\n")
        lines.append("| model | persona | draft_n | accepted | 受理率 |")
        lines.append("|---|---|---:|---:|---:|")
        for mk, pk, total_n, total_ac, rate in draft_rows:
            lines.append(f"| {MODEL_LABEL.get(mk, mk)} | {pk} | {total_n} | {total_ac} | {rate*100:.1f}% |")
        lines.append("")

    return "\n".join(lines)


def main():
    cases = load_cases()
    trials = load_trials()
    idx = index_cases(cases)
    print(f"loaded cases: {len(cases)}, trials: {len(trials)}")

    for p in PERSONA_ORDER:
        grouped_bar(p, idx, os.path.join(OUT_DIR, f"e6_total_{p.lower()}.png"))

    heatmap(idx, "total_elapsed_sec", "E6: C1/C0 と C2/C0 の total elapsed 速度比", os.path.join(OUT_DIR, "e6_speedup_heatmap.png"))
    heatmap(idx, "avg_prompt_tps", "E6: prefill スループット倍率 (C1/C0, C2/C0)", os.path.join(OUT_DIR, "e6_prefill_heatmap.png"))

    per_turn_plots(trials)

    md = markdown_summary(cases, idx, trials)
    summary_path = os.path.join(OUT_DIR, "summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
