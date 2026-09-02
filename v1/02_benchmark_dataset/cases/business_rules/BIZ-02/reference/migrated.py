"""BIZ-02 reference solution: order discount policy (legacy rules ORD-001, ORD-002).

Range check first (rule-file order); discounts strictly over 20 percent require the
acting user's looked-up role to be MGR or ADMIN, where LOOKUP sees live USR_MASTER
rows only (unknown/soft-deleted users have role '').
"""


class BusinessRuleViolation(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


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


def _lookup_role(user_id, users):
    key = "" if user_id is None else str(user_id)
    for u in users:
        if _s(u, "DEL_FLG") != "Y" and _s(u, "USR_ID") == key:  # live rows only
            return _s(u, "ROLE_ID")
    return ""


def set_discount(order, pct, user_id, users):
    p = _n(pct)
    # ORD-001: DISC_PCT >= 0 AND DISC_PCT <= 100 (inclusive boundaries), file order first.
    if not (0 <= p <= 100):
        raise BusinessRuleViolation("E5001", "Discount out of range")
    # ORD-002: > 20 (strict) requires MGR or ADMIN via LOOKUP.
    if p > 20 and _lookup_role(user_id, users) not in ("MGR", "ADMIN"):
        raise BusinessRuleViolation(
            "E5002", "Discount over 20 percent requires manager role")
    updated = dict(order)
    updated["DISC_PCT"] = pct
    return updated
