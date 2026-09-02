#!/usr/bin/env python3
"""Measure per-case prompt input sizes for the cost projection (documented calculation).

v2 (2026-09-01): now builds prompts through the runner's own build_prompt.build() — the
exact strings sent to models — for conditions C1, C2, C3. The v1 heuristic substituted
placeholders across the whole template FILE, whose documentation header repeats the
placeholders, double-counting spec+legacy content (~2x inflation); ledger claim C011 was
corrected accordingly. Token numbers remain a chars/4 heuristic until provider usage fields
supply exact counts (pilot P1).
Writes 05_results/input_size_measurements.csv.
"""
import csv
import json
import sys
from pathlib import Path

V1 = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(V1 / "03_source_code" / "runner"))
from build_prompt import build  # noqa: E402

CASES = V1 / "02_benchmark_dataset" / "cases"
OUT = V1 / "05_results" / "input_size_measurements.csv"


def main():
    rows = []
    for cj in sorted(CASES.glob("*/*/case.json")):
        case = cj.parent
        meta = json.loads(cj.read_text())
        sizes = {}
        for cond in ("C1", "C2", "C3"):
            prompt, _ = build(case, cond, meta)
            sizes[cond] = len(prompt)
        ref_chars = sum(len((case / "reference" / d).read_text())
                        for d in meta["deliverables"])
        rows.append({
            "case_id": meta["id"], "category": meta["category"],
            "difficulty": meta["difficulty"],
            "c1_prompt_chars": sizes["C1"],
            "c2_prompt_chars": sizes["C2"],
            "c3_prompt_chars": sizes["C3"],
            "approx_c1_tokens_chars_div4": sizes["C1"] // 4,
            "approx_c2_tokens_chars_div4": sizes["C2"] // 4,
            "approx_c3_tokens_chars_div4": sizes["C3"] // 4,
            "reference_output_chars": ref_chars,
            "approx_output_tokens_chars_div4": ref_chars // 4,
        })
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    for cond in ("c1", "c2", "c3"):
        t = sum(r[f"approx_{cond}_tokens_chars_div4"] for r in rows)
        print(f"{cond.upper()}: {t:,} approx input tokens per full 36-case pass")
    to = sum(r["approx_output_tokens_chars_div4"] for r in rows)
    print(f"reference-sized output: {to:,} approx tokens per full pass")


if __name__ == "__main__":
    main()
