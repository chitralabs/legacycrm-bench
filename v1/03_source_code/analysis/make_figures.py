#!/usr/bin/env python3
"""Generate the manuscript figure from machine-generated tables (no hand-entered numbers).

F1: two aligned panels over the 12 categories — (a) acceptance tests per category,
(b) mutation kill rate. Single-hue bars (single series ⇒ no legend needed; title names it),
vector PDF (IEEE prefers vector; >300dpi PNG also emitted for the review copy).
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

V1 = Path(__file__).resolve().parent.parent.parent
FT = V1 / "06_figures_tables"

PRETTY = {
    "schema_mapping": "Schema mapping", "validation_rules": "Validation rules",
    "workflows": "Workflows", "legacy_scripts": "Legacy scripts", "rbac": "RBAC",
    "integration": "Integration", "batch_processing": "Batch processing",
    "error_handling": "Error handling", "audit_logging": "Audit logging",
    "referential_integrity": "Referential integrity", "business_rules": "Business rules",
    "config_modernization": "Config. modernization",
}
BAR = "#2E5A87"   # single categorical hue; text stays in ink colors
INK = "#1a1a1a"
MUTED = "#555555"


def rows_of(name):
    with open(FT / name, newline="") as f:
        return [r for r in csv.DictReader(f) if r["category"] != "TOTAL"]


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#cccccc")
    ax.tick_params(colors=MUTED, labelsize=7)
    ax.xaxis.grid(True, color="#e6e6e6", linewidth=0.6)
    ax.set_axisbelow(True)


def main():
    t1 = rows_of("T1_benchmark_composition.csv")
    t3 = {r["category"]: r for r in rows_of("T3_mutation_sensitivity.csv")}
    cats = [r["category"] for r in t1]
    labels = [PRETTY[c] for c in cats]
    tests = [int(r["acceptance_tests"]) for r in t1]
    kill = [float(t3[c]["kill_rate_pct"]) if c in t3 else 0.0 for c in cats]

    # IEEE double-column figure width (7.16 in); constrained layout keeps the long
    # category labels and panel captions inside the canvas (tight_layout clipped them)
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(7.16, 2.9), sharey=True, layout="constrained")
    y = range(len(cats))[::-1]

    ax1.barh(list(y), tests, height=0.62, color=BAR, zorder=3)
    ax1.set_yticks(list(y), labels, fontsize=7, color=INK)
    ax1.set_xlabel("(a) Acceptance tests per category", fontsize=8, color=INK)
    for yi, v in zip(y, tests):
        ax1.text(v + 0.6, yi, str(v), va="center", fontsize=6.5, color=MUTED)
    ax1.set_xlim(0, max(tests) * 1.18)
    style(ax1)

    ax2.barh(list(y), kill, height=0.62, color=BAR, zorder=3)
    ax2.set_xlabel("(b) Mutation kill rate (%)", fontsize=8, color=INK)
    ax2.set_xlim(0, 105)
    for yi, v in zip(y, kill):
        ax2.text(min(v + 1.2, 101), yi, f"{v:.0f}", va="center", fontsize=6.5, color=MUTED)
    style(ax2)

    fig.savefig(FT / "F1_instrument_validation.pdf")
    fig.savefig(FT / "F1_instrument_validation.png", dpi=400)
    # self-contained copy inside the manuscript directory (journal packaging)
    man_fig = V1 / "07_manuscript" / "figures"
    man_fig.mkdir(parents=True, exist_ok=True)
    fig.savefig(man_fig / "F1_instrument_validation.pdf")
    print("wrote F1_instrument_validation.{pdf,png} (+ manuscript copy)")


if __name__ == "__main__":
    main()
