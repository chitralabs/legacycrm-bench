"""BIZ-01 reference solution: credit-hold release guard (legacy rule ACC-004).

Only a Y->N release with CRED_LIMIT > 0 is allowed; a zero/blank/negative limit raises
E1004; a release of an account not on hold is a vacuous no-op (rule never fires).
Audit code CRED_HOLD_OFF on success, per credit_hold_sweep.crms.
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


def release_credit_hold(account):
    updated = dict(account)
    if _s(account, "CRED_HOLD") != "Y":  # blank means 'N': not on hold, vacuous
        return updated, []
    if _n(account.get("CRED_LIMIT")) <= 0:
        raise BusinessRuleViolation(
            "E1004", "Cannot release credit hold with zero credit limit")
    updated["CRED_HOLD"] = "N"
    audits = [{"code": "CRED_HOLD_OFF", "entity_id": _s(account, "ACCT_ID")}]
    return updated, audits
