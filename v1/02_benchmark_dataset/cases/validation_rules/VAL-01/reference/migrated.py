"""VAL-01 reference solution: OPP_MASTER validation rules migrated from Meridian VRL.

Preserves legacy engine semantics (SYSTEM_OVERVIEW.md §2): rule-file order, collect-all
failures, empty-string numeric coercion, NVL defaults, 00000000 date sentinel, event
filtering, BLOCK/WARN severities.
"""

SENTINEL = "00000000"


def _s(record, field):
    v = record.get(field, "")
    return "" if v is None else str(v)


def _n(value):
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _nvl_n(record, field, default):
    v = record.get(field, "")
    if v is None or v == "":
        return default
    return _n(v)


def _date_ge(a, b):
    if a == SENTINEL or b == SENTINEL:
        return False
    return a >= b


def validate(record, old=None, event="INSERT", today="20260901"):
    old = old or {}
    if event == "INSERT":
        old = {}
    errors = []

    def fail(code, message, severity="BLOCK"):
        errors.append({"code": code, "message": message, "severity": severity})

    stat = _s(record, "STAT_CD")
    pct = _n(record.get("STAGE_PCT", ""))
    amt = _nvl_n(record, "AMT", 0)
    close = _s(record, "CLOSE_DT")
    lost = _s(record, "LOST_RSN")

    # OPP-001 ON INSERT,UPDATE : NVL(AMT,0) >= 0
    if not (amt >= 0):
        fail("E3001", "Amount negative")
    # OPP-002 : NOT (STAT_CD='W' AND NVL(AMT,0)=0)
    if stat == "W" and amt == 0:
        fail("E3002", "Won opportunity requires amount")
    # OPP-003 : NOT (STAT_CD='L' AND LOST_RSN='')
    if stat == "L" and lost == "":
        fail("E3003", "Lost reason required")
    # OPP-004 : NOT (STAT_CD='W' AND CLOSE_DT='00000000')
    if stat == "W" and close == SENTINEL:
        fail("E3004", "Won opportunity requires close date")
    # OPP-005 ON UPDATE : NOT (OLD.STAT_CD='W' AND STAT_CD<>'W')
    if event == "UPDATE":
        old_stat = "" if old.get("STAT_CD") is None else str(old.get("STAT_CD", ""))
        if old_stat == "W" and stat != "W":
            fail("E3005", "Cannot reopen a won opportunity")
    # OPP-006 : status/stage-percent consistency
    pairs = {"P": 10, "Q": 25, "N": 60, "W": 100, "L": 0}
    if not (stat in pairs and pct == pairs[stat]):
        fail("E3006", "Stage percent inconsistent with status")
    # OPP-007 ON INSERT, WARN : CLOSE_DT='00000000' OR CLOSE_DT >= TODAY()
    if event == "INSERT":
        if not (close == SENTINEL or _date_ge(close, today)):
            fail("E3007", "Close date in past", "WARN")

    return errors


def is_blocked(errors):
    return any(e["severity"] == "BLOCK" for e in errors)
