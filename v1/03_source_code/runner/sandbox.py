#!/usr/bin/env python3
"""Sandboxed, sanitized execution of candidate solutions (Protocol Amendment A1).

Guarantees per candidate run:
  * SANITIZED case copy: only case.json, tests/, legacy/, target_spec.md are visible.
    reference/ and GROUND_TRUTH.md are never present, so candidate code cannot read the
    oracle's expected values at runtime.
  * NETWORK DENIED: pytest runs under macOS sandbox-exec with a deny-network seatbelt profile.
  * SCRUBBED ENVIRONMENT: explicit whitelist; no API keys or user environment leak into the
    candidate process.
  * RESOURCE LIMITS: CPU-seconds and file-size rlimits via ulimit; wall-clock timeout.

Verified by probe.py (a hostile "candidate" that attempts network, env, and oracle reads).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

V1 = Path(__file__).resolve().parent.parent.parent
HARNESS = V1 / "03_source_code" / "harness"
PROFILE = Path(__file__).resolve().parent / "deny_network.sb"

SANITIZED_ITEMS = ["case.json", "target_spec.md", "tests", "legacy"]
ENV_WHITELIST = {"PATH": "/usr/bin:/bin", "PYTHONHASHSEED": "0", "LANG": "en_US.UTF-8"}


def make_sanitized_copy(case_dir: Path, dest: Path) -> Path:
    """Copy only the non-oracle parts of a case into dest/case."""
    case_copy = dest / "case"
    case_copy.mkdir()
    for item in SANITIZED_ITEMS:
        src = case_dir / item
        if src.is_dir():
            shutil.copytree(src, case_copy / item)
        elif src.is_file():
            shutil.copy(src, case_copy / item)
    assert not (case_copy / "reference").exists()
    assert not (case_copy / "GROUND_TRUTH.md").exists()
    # tests import case_lib (normally provided by cases/conftest.py); ship it locally
    shutil.copy(HARNESS / "case_lib.py", case_copy / "tests" / "case_lib.py")
    return case_copy


def run_sandboxed(case_dir: Path, solution_dir: Path, timeout_s: int = 300,
                  extra_env: dict | None = None) -> dict:
    """Run a case's tests against solution_dir inside the sandbox. Returns a run_case-style dict.

    extra_env: additional whitelisted variables (used by the verification probe only)."""
    case_dir = case_dir.resolve()
    meta = json.loads((case_dir / "case.json").read_text())
    with tempfile.TemporaryDirectory(prefix="lcb_sbx_") as tmp:
        tmpp = Path(tmp)
        case_copy = make_sanitized_copy(case_dir, tmpp)
        sol_copy = tmpp / "solution"
        shutil.copytree(solution_dir, sol_copy)
        report = tmpp / "report.json"
        env = dict(ENV_WHITELIST)
        if extra_env:
            env.update(extra_env)
        env["LCB_SOLUTION_DIR"] = str(sol_copy)
        env["HOME"] = str(tmpp)
        env["TMPDIR"] = str(tmpp)
        import shlex
        py = shlex.quote(sys.executable)  # venv python (carries pytest + plugins)
        inner = (
            f"ulimit -t {timeout_s} -f 51200; "
            f"exec {py} -m pytest {shlex.quote(str(case_copy / 'tests'))} -q --no-header "
            f"-p no:cacheprovider --json-report --json-report-file={shlex.quote(str(report))}"
        )
        cmd = ["/usr/bin/sandbox-exec", "-D", f"HOMEDIR={Path.home()}",
               "-f", str(PROFILE), "/bin/sh", "-c", inner]
        t0 = time.monotonic()
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, env=env,
                                  timeout=timeout_s + 60, cwd=tmpp)
        except subprocess.TimeoutExpired:
            return {"case_id": meta["id"], "category": meta["category"],
                    "difficulty": meta["difficulty"], "num_tests_expected": meta["num_tests"],
                    "num_tests_collected": 0, "num_passed": 0, "pass_rate": 0.0,
                    "all_passed": False, "collection_ok": False, "pytest_exit": None,
                    "infra_error": f"wall_timeout_{timeout_s + 60}s",
                    "wall_seconds": round(time.monotonic() - t0, 3), "tests": []}
        wall = time.monotonic() - t0
        tests = []
        if report.is_file():
            rep = json.loads(report.read_text())
            for t in rep.get("tests", []):
                entry = {"nodeid": t["nodeid"], "outcome": t["outcome"]}
                crash = (t.get("call") or {}).get("crash") or {}
                if crash.get("message"):
                    entry["crash_message"] = crash["message"][:500]
                tests.append(entry)
        passed = sum(1 for t in tests if t["outcome"] == "passed")
        out = {"case_id": meta["id"], "category": meta["category"],
               "difficulty": meta["difficulty"], "num_tests_expected": meta["num_tests"],
               "num_tests_collected": len(tests), "num_passed": passed,
               "pass_rate": (passed / len(tests)) if tests else 0.0,
               "all_passed": bool(tests) and passed == len(tests),
               "collection_ok": len(tests) > 0, "pytest_exit": proc.returncode,
               "wall_seconds": round(wall, 3), "tests": tests}
        if proc.returncode not in (0, 1):
            out["stderr_tail"] = proc.stderr[-2000:]
        return out


def scan_repo_for_keys() -> list:
    """Abort-gate: no credential-looking literals may exist in the repo (excl. venv/archives)."""
    import re
    pat = re.compile(r"sk-[A-Za-z0-9_\-]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (RSA|EC|OPENSSH)")
    hits = []
    for p in V1.rglob("*"):
        parts = set(p.parts)
        if {".venv", "__pycache__", "11_archived_drafts"} & parts or not p.is_file():
            continue
        if p.suffix.lower() in {".png", ".pdf", ".xlsx", ".pyc"}:
            continue
        try:
            if pat.search(p.read_text(errors="ignore")):
                hits.append(str(p))
        except Exception:
            continue
    return hits


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--solution", required=True)
    a = ap.parse_args()
    print(json.dumps(run_sandboxed(Path(a.case), Path(a.solution)), indent=2))
