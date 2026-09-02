"""VAL-03 reference solution: ORD_HEADER/ORD_LINE validation rules with LOOKUP semantics.

Preserves legacy engine semantics (SYSTEM_OVERVIEW.md par.2): rule-file order per table,
collect-all failures, empty-string numeric coercion, OLD.* pre-image on UPDATE, event
filtering, and LOOKUP over live in-memory rows only (soft-deleted rows are invisible;
miss returns the empty string).
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


def _lookup(tables, table, key_col, key_val, out_col):
    rows = (tables or {}).get(table, [])
    for row in rows:
        if _s(row, "DEL_FLG") == "Y":
            continue  # LOOKUP sees live rows only
        if _s(row, key_col) == ("" if key_val is None else str(key_val)):
            return _s(row, out_col)
    return ""


def validate(record, old=None, event="INSERT", tables=None, table="ORD_HEADER"):
    old = old or {}
    if event == "INSERT":
        old = {}
    errors = []

    def fail(code, message, severity="BLOCK"):
        errors.append({"code": code, "message": message, "severity": severity})

    if table == "ORD_HEADER":
        disc = _n(record.get("DISC_PCT", ""))
        stat = _s(record, "STAT_CD")
        # ORD-001 ON INSERT,UPDATE : DISC_PCT >= 0 AND DISC_PCT <= 100
        if not (disc >= 0 and disc <= 100):
            fail("E5001", "Discount out of range")
        if event == "UPDATE":
            # ORD-002 : NOT (DISC_PCT>20 AND role<>'MGR' AND role<>'ADMIN')
            role = _lookup(tables, "USR_MASTER", "USR_ID", _s(record, "OWNER_UID"), "ROLE_ID")
            if disc > 20 and role != "MGR" and role != "ADMIN":
                fail("E5002", "Discount over 20 percent requires manager role")
            # ORD-003 : NOT (OLD.STAT_CD='I' AND STAT_CD<>'I' AND STAT_CD<>'X')
            old_stat = "" if old.get("STAT_CD") is None else str(old.get("STAT_CD", ""))
            if old_stat == "I" and stat != "I" and stat != "X":
                fail("E5003", "Invoiced order can only be cancelled")
    elif table == "ORD_LINE":
        # ORD-004 ON INSERT,UPDATE : QTY > 0
        if not (_n(record.get("QTY", "")) > 0):
            fail("E5004", "Quantity must be positive")
        # ORD-005 ON INSERT : LOOKUP(PROD_MASTER, PROD_ID, PROD_ID, ACTIVE_FLG) = 'Y'
        if event == "INSERT":
            active = _lookup(tables, "PROD_MASTER", "PROD_ID", _s(record, "PROD_ID"),
                             "ACTIVE_FLG")
            if active != "Y":
                fail("E5005", "Product not active")

    return errors


def is_blocked(errors):
    return any(e["severity"] == "BLOCK" for e in errors)
