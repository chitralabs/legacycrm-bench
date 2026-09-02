#!/usr/bin/env python3
"""Sandbox verification probe (Amendment A1 gate).

Runs a hostile 'candidate' through the real sandboxed pipeline (sanitized case copy +
sandbox-exec) and verifies, from INSIDE that context:
  P1 network egress is denied (raw socket and HTTPS both fail)
  P2 the oracle is unreachable (no reference/ dir or GROUND_TRUTH.md anywhere in the
     sandbox tree the candidate can discover by climbing from its own file)
  P3 the environment is scrubbed (no *KEY*/*TOKEN*/*SECRET*/*PASS* variables)
plus, from outside: tests actually ran, and the hostile no-op candidate does not pass them.
Exit 0 = sandbox verified. Run before any model call (release gate).
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sandbox import run_sandboxed, V1

PROBE_SOLUTION = r'''
import json, os, socket
from pathlib import Path

findings = {"socket": "?", "https": "?", "oracle_paths_found": None, "secretish_env": None}
try:
    s = socket.create_connection(("1.1.1.1", 443), timeout=3); s.close()
    findings["socket"] = "CONNECTED (SANDBOX FAILURE)"
except Exception as e:
    findings["socket"] = f"blocked: {type(e).__name__}"
try:
    import urllib.request
    urllib.request.urlopen("https://example.com", timeout=3).read(10)
    findings["https"] = "FETCHED (SANDBOX FAILURE)"
except Exception as e:
    findings["https"] = f"blocked: {type(e).__name__}"
# climb from the candidate file to the sandbox temp root and hunt for oracle files
here = Path(__file__).resolve()
root = here.parents[1]  # <tmp>/ containing solution/ and case/
hits = [str(p) for p in root.rglob("reference")] + [str(p) for p in root.rglob("GROUND_TRUTH.md")]
findings["oracle_paths_found"] = hits
findings["secretish_env"] = sorted(
    k for k in os.environ
    if any(t in k.upper() for t in ("KEY", "TOKEN", "SECRET", "PASS")))
# P4: credential-bearing user files must be unreadable at their REAL path
# (HOME is scrubbed to the tmp dir, so use the true home passed by the probe harness)
real_home = os.environ.get("LCB_REAL_HOME", "")
try:
    open(real_home + "/.zshrc").read(10)
    findings["zshrc_read"] = "READ (SANDBOX FAILURE)"
except Exception as e:
    findings["zshrc_read"] = f"blocked: {type(e).__name__}"
out = os.environ.get("LCB_PROBE_OUT")
if out:
    Path(out).write_text(json.dumps(findings))

def validate(record, old=None, event="INSERT", today="20260901"):
    return []
def is_blocked(errors):
    return False
'''


def main():
    case = V1 / "02_benchmark_dataset" / "cases" / "validation_rules" / "VAL-01"
    with tempfile.TemporaryDirectory(prefix="lcb_probe_") as tmp:
        sol = Path(tmp) / "probe_solution"
        sol.mkdir()
        (sol / "migrated.py").write_text(PROBE_SOLUTION)
        report_path = Path(tmp) / "probe_report.json"
        res = run_sandboxed(case, sol, extra_env={"LCB_PROBE_OUT": str(report_path),
                                                  "LCB_REAL_HOME": str(Path.home())})
        if not report_path.is_file():
            print("PROBE ERROR: hostile candidate never executed (no report)")
            print(json.dumps(res, indent=2))
            sys.exit(2)
        f = json.loads(report_path.read_text())
    checks = [
        ("network socket denied", f["socket"].startswith("blocked")),
        ("network https denied", f["https"].startswith("blocked")),
        ("no oracle files reachable in sandbox tree", f["oracle_paths_found"] == []),
        ("no secret-like env vars visible", f["secretish_env"] == []),
        ("shell profile (~/.zshrc) unreadable", f.get("zshrc_read", "?").startswith("blocked")),
        ("acceptance tests executed against probe", res["num_tests_collected"] > 0),
        ("hostile no-op candidate does NOT pass acceptance", not res["all_passed"]),
    ]
    ok = True
    for name, passed in checks:
        print(("PASS " if passed else "FAIL ") + name)
        ok &= passed
    print("probe findings:", json.dumps(f))
    print("acceptance result:", res["num_passed"], "/", res["num_tests_collected"])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
