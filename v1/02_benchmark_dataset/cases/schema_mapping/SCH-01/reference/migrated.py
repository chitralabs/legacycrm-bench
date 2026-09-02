"""SCH-01 reference solution: ACCT_MASTER -> modern `account` mapping.

Preserves legacy conventions (SYSTEM_OVERVIEW.md par.1): 00000000 date sentinel -> None,
CHAR(1) Y/N booleans (blank=N), blank CURR_CD -> USD, blank numerics -> 0, soft-deleted
rows (DEL_FLG='Y') -> None.
"""

SENTINEL = "00000000"


def _s(row, col):
    v = row.get(col, "")
    return "" if v is None else str(v)


def _date(row, col):
    v = _s(row, col)
    if v == "" or v == SENTINEL:
        return None
    return f"{v[0:4]}-{v[4:6]}-{v[6:8]}"


def _num(row, col):
    v = _s(row, col)
    if v == "":
        return 0.0
    return float(v)


def _yn(row, col):
    return _s(row, col) == "Y"


def convert_account(row):
    if _s(row, "DEL_FLG") == "Y":
        return None
    return {
        "account_id": _s(row, "ACCT_ID"),
        "name": _s(row, "ACCT_NM"),
        "account_type": _s(row, "ACCT_TYP"),
        "sic_code": _s(row, "SIC_CD"),
        "region": _s(row, "REGION_CD"),
        "annual_revenue": _num(row, "ANN_REV"),
        "currency": _s(row, "CURR_CD") or "USD",
        "owner_id": _s(row, "OWNER_UID"),
        "team_code": _s(row, "TEAM_CD"),
        "credit_limit": _num(row, "CRED_LIMIT"),
        "credit_hold": _yn(row, "CRED_HOLD"),
        "created_date": _date(row, "CREATE_DT"),
        "updated_date": _date(row, "UPD_DT"),
    }
