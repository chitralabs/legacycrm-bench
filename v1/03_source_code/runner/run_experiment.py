#!/usr/bin/env python3
"""LegacyCRM-Bench experiment orchestrator (conditions C1-C4, sandboxed, spend-capped).

Usage:
  python run_experiment.py --config ../../04_experiments/run_config.json \
      --run-id P1_pilot --models sonnet46 --conditions C1 --runs 1 [--cases VAL-01,RBC-02]

Startup gates (all must pass or the runner refuses to start):
  * repo credential scan clean (sandbox.scan_repo_for_keys)
  * sandbox probe passes (probe.py) — cached marker 05_results/sandbox_probe_ok.json (<24h)
  * config prices carry a retrieval date; hard cap present
Per call: prompt/response SHA-256, usage, latency, cost estimate appended to the spend ledger
(04_experiments/spend_ledger.json); the runner HALTS before any call once
spent + worst_case_next > cap. Raw responses stored immutably under
04_experiments/raw_outputs/<run_id>/. Results appended to 05_results/model_runs/<run_id>.jsonl.
C4: initial C2 call + up to 2 repair rounds with redacted failure feedback.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

RUNNER = Path(__file__).resolve().parent
sys.path.insert(0, str(RUNNER))
from build_prompt import build  # noqa: E402
from extract_files import extract  # noqa: E402
from model_client import call_model, estimate_cost_usd, get_key  # noqa: E402
from redact_failures import build_feedback, leakage_scan  # noqa: E402
from sandbox import run_sandboxed, scan_repo_for_keys, V1  # noqa: E402

CASES = V1 / "02_benchmark_dataset" / "cases"
LEDGER = V1 / "04_experiments" / "spend_ledger.json"
PROBE_MARKER = V1 / "05_results" / "sandbox_probe_ok.json"


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


LEDGER_LOCK = LEDGER.with_suffix(".lock")


def _locked(fn):
    """Run fn() while holding an exclusive flock (safe across parallel model processes)."""
    import fcntl
    LEDGER_LOCK.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            return fn()
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)


def ledger_spent() -> float:
    def read():
        if LEDGER.is_file():
            return json.loads(LEDGER.read_text())["spent_usd"]
        return 0.0
    return _locked(read)


def ledger_add(cost: float) -> float:
    """Atomically add a call's cost; returns the new cumulative spend."""
    def update():
        led = (json.loads(LEDGER.read_text()) if LEDGER.is_file()
               else {"spent_usd": 0.0, "calls": 0})
        led["spent_usd"] = round(led["spent_usd"] + cost, 6)
        led["calls"] += 1
        LEDGER.write_text(json.dumps(led, indent=2))
        return led["spent_usd"]
    return _locked(update)


def ensure_gates(cfg, models):
    hits = scan_repo_for_keys()
    if hits:
        sys.exit(f"ABORT: credential-like literals in repo: {hits}")
    fresh = False
    if PROBE_MARKER.is_file():
        m = json.loads(PROBE_MARKER.read_text())
        fresh = (time.time() - m["ts"]) < 86400 and m.get("ok")
    if not fresh:
        print("running sandbox probe ...")
        r = subprocess.run([sys.executable, str(RUNNER / "probe.py")],
                          capture_output=True, text=True)
        ok = r.returncode == 0
        PROBE_MARKER.write_text(json.dumps({"ok": ok, "ts": time.time(),
                                            "output": r.stdout[-2000:]}))
        if not ok:
            sys.exit("ABORT: sandbox probe FAILED:\n" + r.stdout + r.stderr)
        print("sandbox probe OK")
    if "prices_verified" not in cfg or "cap_usd" not in cfg:
        sys.exit("ABORT: config missing prices_verified/cap_usd")
    for m in models:
        if not m["provider"].startswith("mock") and not get_key(m["provider"]):
            sys.exit(f"ABORT: no API key available for provider {m['provider']} "
                     f"(env or Keychain service lcb_{m['provider']})")


def iter_cases(only=None):
    for cj in sorted(CASES.glob("*/*/case.json")):
        meta = json.loads(cj.read_text())
        if only and meta["id"] not in only:
            continue
        yield cj.parent, meta


def one_generation(model_cfg, case_dir, meta, condition, run_idx, raw_dir, cap, worst_next):
    spent = ledger_spent()
    if spent + worst_next > cap:
        raise BudgetExceeded(f"cap {cap} would be exceeded (spent {spent:.2f})")
    prompt, plog = build(case_dir, condition, meta)
    model_cfg = dict(model_cfg, _case_dir=str(case_dir))
    rec = call_with_retry(model_cfg, prompt, seed=run_idx)
    cost = estimate_cost_usd(model_cfg, rec)
    ledger_add(cost)
    raw_path = raw_dir / f"{meta['id']}_{condition}_r{run_idx}_{int(time.time()*1000)}.json"
    raw_path.write_text(json.dumps({"prompt_sha256": sha(prompt), "prompt_log": plog,
                                    "response": rec["raw"], "text": rec["text"]}, default=str))
    return prompt, plog, rec, cost, raw_path


class BudgetExceeded(RuntimeError):
    pass


class CreditsExhausted(RuntimeError):
    pass


def call_with_retry(model_cfg, prompt, seed=None):
    """Protocol §6: up to 3 retries with exponential backoff on transient API errors.
    Credit exhaustion halts the arm cleanly (no point retrying); persistent transient
    failure raises TransientFailed so the caller records an infra_error row."""
    import openai
    delays = [10, 30, 90]
    last = None
    for attempt in range(4):
        try:
            return call_model(model_cfg, prompt, seed=seed)
        except openai.RateLimitError as e:
            if "insufficient_quota" in str(e) or "credit_balance_exhausted" in str(e):
                raise CreditsExhausted(str(e)[:200])
            last = e
        except (openai.APIConnectionError, openai.InternalServerError,
                openai.APITimeoutError) as e:
            last = e
        if attempt < 3:
            time.sleep(delays[attempt])
    raise TransientFailed(f"{type(last).__name__}: {str(last)[:200]}")


class TransientFailed(RuntimeError):
    pass


def completed_cells(out_path: Path) -> set:
    """(model_key, condition, run_index, case_id) tuples already recorded — resume support."""
    done = set()
    if out_path.is_file():
        for line in open(out_path):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "_meta" in d or "_halt" in d:
                continue
            if d.get("result", {}).get("infra_error"):
                continue  # infra_error cells are retried on resume
            done.add((d["model_key"], d["condition"], d["run_index"], d["result"]["case_id"]))
    return done


def evaluate(case_dir, meta, text):
    files, notes = extract(text, meta["deliverables"])
    with tempfile.TemporaryDirectory(prefix="lcb_cand_") as tmp:
        sol = Path(tmp) / "sol"
        sol.mkdir()
        for name, content in files.items():
            (sol / name).write_text(content)
        res = run_sandboxed(case_dir, sol) if files else {
            "case_id": meta["id"], "category": meta["category"], "difficulty": meta["difficulty"],
            "num_tests_expected": meta["num_tests"], "num_tests_collected": 0, "num_passed": 0,
            "pass_rate": 0.0, "all_passed": False, "collection_ok": False,
            "pytest_exit": None, "wall_seconds": 0.0, "tests": [],
            "build_failure": "no deliverable files extracted"}
    res["extract_notes"] = notes
    res["deliverables_extracted"] = sorted(files)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--models", required=True, help="comma-separated model keys from config")
    ap.add_argument("--conditions", required=True, help="e.g. C1,C2,C3 or C4")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--cases", default=None)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    models = [dict(cfg["models"][k], key=k) for k in args.models.split(",")]
    conditions = args.conditions.split(",")
    only = set(args.cases.split(",")) if args.cases else None
    ensure_gates(cfg, models)

    cap = float(cfg["cap_usd"])
    raw_dir = V1 / "04_experiments" / "raw_outputs" / args.run_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir = V1 / "05_results" / "model_runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{args.run_id}.jsonl"
    mode = "a" if out.is_file() else "w"
    done = completed_cells(out)
    if done:
        print(f"resume: {len(done)} completed cells found; they will be skipped")
    worst_next = float(cfg.get("worst_case_call_usd", 3.0))

    with open(out, mode) as f:
        if mode == "w":
            f.write(json.dumps({"_meta": {
                "run_id": args.run_id, "config_sha256": sha(json.dumps(cfg, sort_keys=True)),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "models": {m["key"]: {kk: m.get(kk) for kk in ("provider", "id")} for m in models},
                "conditions": conditions, "runs": args.runs,
                "prices_verified": cfg["prices_verified"], "cap_usd": cap}}) + "\n")
        try:
            for model_cfg in models:
                for case_dir, meta in iter_cases(only):
                    for condition in conditions:
                        for run_idx in range(args.runs):
                            if (model_cfg["key"], condition, run_idx, meta["id"]) in done:
                                continue
                            t0 = time.monotonic()
                            base_cond = "C2" if condition == "C4" else condition
                            try:
                                prompt, plog, rec, cost, raw_path = one_generation(
                                    model_cfg, case_dir, meta, base_cond, run_idx,
                                    raw_dir, cap, worst_next)
                            except TransientFailed as te:
                                f.write(json.dumps({
                                    "run_id": args.run_id, "model_key": model_cfg["key"],
                                    "model_id": model_cfg["id"],
                                    "provider": model_cfg["provider"],
                                    "condition": condition, "run_index": run_idx,
                                    "result": {"case_id": meta["id"],
                                               "category": meta["category"],
                                               "difficulty": meta["difficulty"],
                                               "infra_error": str(te), "all_passed": False,
                                               "num_passed": 0, "num_tests_collected": 0,
                                               "tests": []},
                                    "cost_usd": 0.0}) + "\n")
                                f.flush()
                                print(f"{model_cfg['key']:>10} {condition} r{run_idx} "
                                      f"{meta['id']:8s} INFRA_ERROR {te}")
                                continue
                            res = evaluate(case_dir, meta, rec["text"])
                            repairs = []
                            if condition == "C4":
                                for r_i in range(2):
                                    if res["all_passed"]:
                                        break
                                    fb = build_feedback(res)
                                    rp = (prompt + "\n\nYour previous migration failed "
                                          "acceptance testing. Failing checks (assertion "
                                          "details redacted):\n\n" + fb +
                                          "\n\nRevise and output the complete corrected "
                                          "deliverable file(s) again, in the same "
                                          "```file:<name> fenced-block format. Output "
                                          "nothing else.\n\nYour previous answer:\n\n"
                                          + rec["text"])
                                    if ledger_spent() + worst_next > cap:
                                        raise BudgetExceeded("cap during repair")
                                    rec2 = call_model(dict(model_cfg, _case_dir=str(case_dir)), rp)
                                    cost2 = estimate_cost_usd(model_cfg, rec2)
                                    ledger_add(cost2)
                                    rp_path = raw_dir / (raw_path.stem + f"_repair{r_i}.json")
                                    rp_path.write_text(json.dumps(
                                        {"prompt_sha256": sha(rp), "feedback": fb,
                                         "response": rec2["raw"], "text": rec2["text"]},
                                        default=str))
                                    repairs.append({"feedback_sha256": sha(fb), "cost_usd": cost2,
                                                    "output_tokens": rec2["output_tokens"]})
                                    rec = rec2
                                    res = evaluate(case_dir, meta, rec["text"])
                            row = {"run_id": args.run_id, "model_key": model_cfg["key"],
                                   "model_id": model_cfg["id"], "provider": model_cfg["provider"],
                                   "condition": condition, "run_index": run_idx,
                                   "prompt_sha256": sha(prompt), "prompt_log": plog,
                                   "response_sha256": sha(rec["text"]),
                                   "input_tokens": rec["input_tokens"],
                                   "output_tokens": rec["output_tokens"],
                                   "cache_read_tokens": rec.get("cache_read_tokens", 0),
                                   "latency_s": rec["latency_s"],
                                   "cost_usd": round(cost + sum(r["cost_usd"] for r in repairs), 6),
                                   "repairs": repairs,
                                   "stop_reason": rec.get("stop_reason"),
                                   "params": rec["params"],
                                   "wall_s_total": round(time.monotonic() - t0, 3),
                                   "result": res}
                            f.write(json.dumps(row, default=str) + "\n")
                            f.flush()
                            print(f"{model_cfg['key']:>10} {condition} r{run_idx} "
                                  f"{meta['id']:8s} {res['num_passed']:>3}/"
                                  f"{res['num_tests_collected']:<3} "
                                  f"${ledger_spent():.2f} spent")
        except BudgetExceeded as e:
            print(f"HALT: {e}")
            f.write(json.dumps({"_halt": str(e), "spent_usd": ledger_spent()}) + "\n")
        except CreditsExhausted as e:
            print(f"HALT (account credits exhausted): {e}")
            f.write(json.dumps({"_halt": f"credits_exhausted: {e}",
                                "spent_usd": ledger_spent()}) + "\n")
    print(f"\ndone. total spent (all runs): ${ledger_spent():.2f} of cap ${cap}")


if __name__ == "__main__":
    main()
