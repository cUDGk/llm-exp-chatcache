"""
dump_transcripts.py -- conv_trials.jsonl から (model, persona) ごとに読みやすい
markdown トランスクリプトを生成する。

temp=0 seed=42 なので C0/C1/C2 の content は同一 → C0 の応答だけ使う。
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

# dedupe: failed runs leave partial trials before a later full run appends.
# keep the LAST appearance of each (case_id, turn).
latest = {}
with open(TRIALS, encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        t = json.loads(line)
        latest[(t["case_id"], t["turn"])] = t
by_case = defaultdict(list)
for (cid, _), t in latest.items():
    by_case[cid].append(t)

for case_id, rows in by_case.items():
    if not case_id.endswith("-C0"):
        continue
    rows.sort(key=lambda r: r["turn"])
    _, mk, pk, _ = case_id.split("-")
    model = MODEL_LABEL.get(mk, mk)
    persona = PERSONA_LABEL.get(pk, pk)

    lines = [f"# {model} × {persona}", ""]
    lines.append(f"- case: `{case_id}` (C0 baseline の 20 ターン)")
    total_p = sum(r.get("prompt_tokens") or 0 for r in rows)
    total_g = sum(r.get("gen_tokens") or 0 for r in rows)
    avg_gen_tps = sum((r.get("gen_tps") or 0) for r in rows) / len(rows)
    lines.append(f"- 合計トークン: prompt={total_p}, gen={total_g}")
    lines.append(f"- 平均 gen: {avg_gen_tps:.1f} tok/s")
    lines.append("")

    for r in rows:
        lines.append(f"## Turn {r['turn']}  _(elapsed {r['elapsed_sec']:.1f}s / gen {r.get('gen_tps') or 0:.1f} tok/s)_")
        lines.append("")
        lines.append(f"**User**: {r['user']}")
        lines.append("")
        assistant = (r.get("assistant") or "").strip()
        lines.append("**Assistant**:")
        lines.append("")
        for ln in assistant.splitlines():
            lines.append(f"> {ln}" if ln else ">")
        lines.append("")

    out_path = os.path.join(OUT_DIR, f"{mk}_{pk}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {out_path}")
