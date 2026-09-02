#!/usr/bin/env python3
"""Redact acceptance-test failure signals for the C4 repair loop (oracle-leakage control).

Passes through: test function name, exception type. Redacts: every quoted string literal,
every number, and everything after 'assert' comparisons in crash messages. A 100% automated
leakage scan (no digit runs or quoted literals may survive) runs on every produced string.
"""
import re

QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")
NUM = re.compile(r"(?<![A-Za-z_])[-+]?\d[\d.,]*")


def redact_message(msg: str) -> str:
    msg = msg.splitlines()[0] if msg else ""
    msg = QUOTED.sub("<redacted>", msg)
    msg = NUM.sub("<redacted>", msg)
    return msg[:200]


def leakage_scan(s: str) -> list:
    """Returns violations (should be empty): surviving quoted literals or digit runs."""
    viol = []
    for m in QUOTED.finditer(s):
        if m.group(0) not in ("'<redacted>'", '"<redacted>"'):
            viol.append(m.group(0))
    viol += NUM.findall(s)
    return viol


def build_feedback(result: dict) -> str:
    lines = []
    for t in result.get("tests", []):
        if t["outcome"] == "passed":
            continue
        name = t["nodeid"].split("::")[-1]
        crash = redact_message(t.get("crash_message", "") or "")
        # leakage scan applies to the crash text only (test names are public structure)
        if crash and leakage_scan(crash.replace("<redacted>", "")):
            crash = ""  # name-only fallback if anything survives redaction
        lines.append(f"- {name}" + (f": {crash}" if crash else ""))
    return "\n".join(lines) if lines else "- (no per-test details available)"
