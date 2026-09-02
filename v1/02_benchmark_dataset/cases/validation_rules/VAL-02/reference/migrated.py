"""VAL-02 reference solution: ACCT_MASTER validation rules migrated from Meridian VRL.

Preserves legacy engine semantics (SYSTEM_OVERVIEW.md par.2): rule-file order, collect-all
failures, empty-string numeric coercion, NVL defaults, OLD.* pre-image on UPDATE (empty on
INSERT), event filtering, BLOCK/WARN severities.
"""


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


def validate(record, old=None, event="INSERT", today="20260901"):
    old = old or {}
    if event == "INSERT":
        old = {}
    errors = []

    def fail(code, message, severity="BLOCK"):
        errors.append({"code": code, "message": message, "severity": severity})

    name = _s(record, "ACCT_NM")
    typ = _s(record, "ACCT_TYP")
    region = _s(record, "REGION_CD")
    cred_hold = _s(record, "CRED_HOLD")
    cred_limit = _n(record.get("CRED_LIMIT", ""))

    # ACC-001 ON INSERT,UPDATE : LEN(ACCT_NM) >= 2
    if not (len(name) >= 2):
        fail("E1001", "Account name too short")
    # ACC-002 : ACCT_TYP in {C, P, R, X}
    if typ not in ("C", "P", "R", "X"):
        fail("E1002", "Invalid account type")
    # ACC-003 : NVL(ANN_REV, 0) >= 0
    if not (_nvl_n(record, "ANN_REV", 0) >= 0):
        fail("E1003", "Annual revenue negative")
    # ACC-004 ON UPDATE : NOT (OLD.CRED_HOLD='Y' AND CRED_HOLD='N' AND CRED_LIMIT<=0)
    if event == "UPDATE":
        old_hold = "" if old.get("CRED_HOLD") is None else str(old.get("CRED_HOLD", ""))
        if old_hold == "Y" and cred_hold == "N" and cred_limit <= 0:
            fail("E1004", "Cannot release credit hold with zero credit limit")
    # ACC-005 : LEN(REGION_CD) = 3, SEVERITY WARN
    if not (len(region) == 3):
        fail("E1005", "Region code must be 3 chars", "WARN")

    return errors


def is_blocked(errors):
    return any(e["severity"] == "BLOCK" for e in errors)
