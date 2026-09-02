"""SCR-02 reference solution: credit_hold_sweep.crms migrated to a Python sweep service.

Preserves legacy semantics (SYSTEM_OVERVIEW.md §4 + credit_hold_sweep.crms): live 'C'
accounts only, primary-key-ascending processing order, invoiced live orders only in the
exposure, hold when exposure > limit, release only when exposure <= 80% of limit
(hysteresis band between 80% and 100%), sequential IF evaluation, exact decimal math.
"""
from decimal import Decimal


def _d(value):
    """NVL(x, 0) with legacy empty-string coercion, as an exact Decimal."""
    if value is None or value == "":
        return Decimal(0)
    try:
        return Decimal(str(value))
    except ArithmeticError:
        return Decimal(0)
    except ValueError:
        return Decimal(0)


def _s(row, field):
    v = row.get(field, "")
    return "" if v is None else str(v)


def sweep(accounts, orders):
    new_accounts = [dict(a) for a in accounts]
    live_orders = [o for o in orders if _s(o, "DEL_FLG") != "Y"]
    audits = []

    eligible = [a for a in new_accounts
                if _s(a, "DEL_FLG") != "Y" and _s(a, "ACCT_TYP") == "C"]
    # FOR EACH iterates live rows ordered by primary key ascending (§4).
    for acct in sorted(eligible, key=lambda a: _s(a, "ACCT_ID")):
        acct_id = _s(acct, "ACCT_ID")
        exposure = Decimal(0)
        for ord_row in live_orders:
            if _s(ord_row, "ACCT_ID") == acct_id and _s(ord_row, "STAT_CD") == "I":
                exposure += _d(ord_row.get("TOT_AMT"))
        limit = _d(acct.get("CRED_LIMIT"))

        if exposure > limit and _s(acct, "CRED_HOLD") != "Y":
            acct["CRED_HOLD"] = "Y"
            audits.append(("CRED_HOLD_ON", acct_id))
        if exposure <= limit * Decimal(8) / Decimal(10) and _s(acct, "CRED_HOLD") == "Y":
            # release only when exposure drops to/below 80% of limit (hysteresis)
            acct["CRED_HOLD"] = "N"
            audits.append(("CRED_HOLD_OFF", acct_id))

    return new_accounts, audits
