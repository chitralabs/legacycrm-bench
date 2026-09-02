#!/usr/bin/env python3
"""Statistical analysis of model runs per STUDY_PROTOCOL.md §2/§5 (+A1/A2).

Reads 05_results/model_runs/*.jsonl and the frozen tag map 05_results/test_tags.csv.
Implements the frozen unit-of-analysis rule: k runs collapse to one case-level outcome by
majority; pass^k and all-k-agree reported separately. Wilson CIs; paired bootstrap (10k,
case resampling) for condition deltas; McNemar exact tests with Holm-Bonferroni across the
condition-pair family per model. Category-level output is descriptive only.

Outputs (06_figures_tables/): M1_case_allpass.csv, M2_condition_deltas.csv,
M3_property_class.csv, M4_reliability.csv, M5_cost_latency.csv, run_disposition.csv
"""
import csv
import itertools
import json
import math
import random
from collections import defaultdict
from pathlib import Path

V1 = Path(__file__).resolve().parent.parent.parent
RUNS = V1 / "05_results" / "model_runs"
TAGS = V1 / "05_results" / "test_tags.csv"
OUT = V1 / "06_figures_tables"

Z = 1.959964


def wilson(k, n):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    den = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / den
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return p, max(0.0, c - h), min(1.0, c + h)


def mcnemar_exact(b, c):
    """Two-sided exact McNemar on discordant counts b, c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def holm(pvals):
    """pvals: dict key->p. Returns dict key->adjusted p (Holm-Bonferroni)."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, prev = {}, 0.0
    for i, (k, p) in enumerate(items):
        a = min(1.0, (m - i) * p)
        prev = max(prev, a)
        adj[k] = prev
    return adj


# P1_pilot is the calibration/gating run (protocol: "P1 gates P2"); it is excluded from
# inference so terra's C1 cells keep exactly k=5 runs like every other cell.
EXCLUDED_RUN_IDS = {"P1_pilot"}


def load_rows(exclude_mock=True):
    rows = []
    for f in sorted(RUNS.glob("*.jsonl")):
        for line in open(f):
            d = json.loads(line)
            if "_meta" in d or "_halt" in d:
                continue
            if exclude_mock and d["provider"].startswith("mock"):
                continue
            if d.get("run_id") in EXCLUDED_RUN_IDS:
                continue
            rows.append(d)
    return rows


def load_tags():
    tags = {}
    if TAGS.is_file():
        for r in csv.DictReader(open(TAGS)):
            tags[(r["case_id"], r["test_name"])] = r["proposed_class" if "final_class" not in r else "final_class"]
    return tags


def main():
    OUT.mkdir(exist_ok=True)
    rows = load_rows()
    if not rows:
        print("no model-run rows found (mock runs are excluded); nothing to analyze")
        return
    tags = load_tags()

    # disposition
    disp = defaultdict(int)
    ok_rows = []
    for r in rows:
        res = r["result"]
        if res.get("infra_error"):
            disp[(r["model_key"], r["condition"], "infra_error")] += 1
        else:
            disp[(r["model_key"], r["condition"], "completed")] += 1
            ok_rows.append(r)
    with open(OUT / "run_disposition.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["model", "condition", "disposition", "count"])
        for (m, c, d), n in sorted(disp.items()):
            w.writerow([m, c, d, n])

    # collapse k runs -> case outcome by majority (frozen rule)
    cell = defaultdict(list)  # (model, cond, case) -> [all_passed...]
    for r in ok_rows:
        cell[(r["model_key"], r["condition"], r["result"]["case_id"])].append(
            bool(r["result"]["all_passed"]))
    collapsed = {}
    for key, outcomes in cell.items():
        collapsed[key] = sum(outcomes) > len(outcomes) / 2

    models = sorted({k[0] for k in collapsed})
    conds = sorted({k[1] for k in collapsed})
    cases = sorted({k[2] for k in collapsed})

    with open(OUT / "M1_case_allpass.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["model", "condition", "cases", "all_pass", "rate", "wilson_lo", "wilson_hi"])
        for m in models:
            for c in conds:
                outs = [collapsed[(m, c, cs)] for cs in cases if (m, c, cs) in collapsed]
                if not outs:
                    continue  # condition not run for this model (e.g., C4 is sol+terra only)
                p, lo, hi = wilson(sum(outs), len(outs))
                w.writerow([m, c, len(outs), sum(outs), f"{p:.4f}", f"{lo:.4f}", f"{hi:.4f}"])

    # paired condition deltas per model: bootstrap + McNemar + Holm
    rng = random.Random(20260901)
    with open(OUT / "M2_condition_deltas.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["model", "cond_a", "cond_b", "n_paired", "delta", "boot_lo", "boot_hi",
                    "discordant_b", "discordant_c", "mcnemar_p", "holm_p", "underpowered_flag"])
        for m in models:
            pvals, meta_rows = {}, []
            for ca, cb in itertools.combinations(conds, 2):
                paired = [(collapsed.get((m, ca, cs)), collapsed.get((m, cb, cs)))
                          for cs in cases]
                paired = [(a, b) for a, b in paired if a is not None and b is not None]
                if not paired:
                    continue
                delta = (sum(b for _, b in paired) - sum(a for a, _ in paired)) / len(paired)
                boots = []
                for _ in range(10000):
                    samp = [paired[rng.randrange(len(paired))] for _ in paired]
                    boots.append((sum(b for _, b in samp) - sum(a for a, _ in samp)) / len(samp))
                boots.sort()
                lo, hi = boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots))]
                b_ = sum(1 for a, b in paired if (not a) and b)
                c_ = sum(1 for a, b in paired if a and (not b))
                p = mcnemar_exact(b_, c_)
                pvals[(ca, cb)] = p
                meta_rows.append([m, ca, cb, len(paired), delta, lo, hi, b_, c_, p])
            adj = holm(pvals) if pvals else {}
            for row in meta_rows:
                key = (row[1], row[2])
                under = "yes" if (row[7] + row[8]) < 8 else ""
                w.writerow(row[:4] + [f"{row[4]:.3f}", f"{row[5]:.3f}", f"{row[6]:.3f}",
                                      row[7], row[8], f"{row[9]:.4f}",
                                      f"{adj.get(key, 1.0):.4f}", under])

    # property classes (majority-collapsed per test across k runs)
    tcell = defaultdict(list)  # (model, cond, case, test) -> [passed...]
    for r in ok_rows:
        for t in r["result"]["tests"]:
            name = t["nodeid"].split("::")[-1]
            tcell[(r["model_key"], r["condition"], r["result"]["case_id"], name)].append(
                t["outcome"] == "passed")
    with open(OUT / "M3_property_class.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["model", "condition", "property_class", "tests", "passed", "rate_descriptive"])
        agg = defaultdict(lambda: [0, 0])
        for (m, c, cs, tn), outs in tcell.items():
            klass = tags.get((cs, tn), "untagged")
            a = agg[(m, c, klass)]
            a[0] += 1
            a[1] += int(sum(outs) > len(outs) / 2)
        for (m, c, k), (n, p) in sorted(agg.items()):
            w.writerow([m, c, k, n, p, f"{p / n:.3f}" if n else ""])

    # reliability: pass^k and all-k-agree
    with open(OUT / "M4_reliability.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["model", "condition", "k", "pass_all_k_rate", "all_k_agree_rate"])
        for m in models:
            for c in conds:
                ks = [len(v) for key, v in cell.items() if key[0] == m and key[1] == c]
                if not ks:
                    continue
                k = max(ks)
                cells_ = [v for key, v in cell.items() if key[0] == m and key[1] == c]
                passk = sum(1 for v in cells_ if all(v)) / len(cells_)
                agree = sum(1 for v in cells_ if len(set(v)) == 1) / len(cells_)
                w.writerow([m, c, k, f"{passk:.3f}", f"{agree:.3f}"])

    # cost / latency
    with open(OUT / "M5_cost_latency.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["model", "condition", "calls", "input_tokens", "output_tokens",
                    "cache_read_tokens", "cost_usd", "mean_latency_s"])
        agg = defaultdict(lambda: [0, 0, 0, 0, 0.0, 0.0])
        for r in ok_rows:
            a = agg[(r["model_key"], r["condition"])]
            a[0] += 1 + len(r.get("repairs", []))
            a[1] += r["input_tokens"]
            a[2] += r["output_tokens"]
            a[3] += r.get("cache_read_tokens", 0)
            a[4] += r["cost_usd"]
            a[5] += r["latency_s"]
        for (m, c), (n, ti, to, cr, cost, lat) in sorted(agg.items()):
            w.writerow([m, c, n, ti, to, cr, f"{cost:.4f}", f"{lat / max(1, n):.2f}"])

    print("model analysis tables written to", OUT)


if __name__ == "__main__":
    main()
