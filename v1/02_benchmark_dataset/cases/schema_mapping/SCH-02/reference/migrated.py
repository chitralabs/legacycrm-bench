"""SCH-02 reference solution: CONT_MASTER -> modern `contact` mapping.

Legacy conventions (SYSTEM_OVERVIEW.md par.1): PREF_CH enum with blank=E, OPTOUT_FLG Y/N
boolean (blank=N), blank EMAIL_TX -> None, 00000000 date sentinel -> None, soft-deleted
rows dropped; convert_all preserves input order of surviving rows.
"""

SENTINEL = "00000000"
PREF_CHANNELS = {"E": "email", "P": "phone", "M": "mail"}


def _s(row, col):
    v = row.get(col, "")
    return "" if v is None else str(v)


def _date(row, col):
    v = _s(row, col)
    if v == "" or v == SENTINEL:
        return None
    return f"{v[0:4]}-{v[4:6]}-{v[6:8]}"


def convert_contact(row):
    if _s(row, "DEL_FLG") == "Y":
        return None
    pref = _s(row, "PREF_CH")
    email = _s(row, "EMAIL_TX")
    return {
        "contact_id": _s(row, "CONT_ID"),
        "account_id": _s(row, "ACCT_ID"),
        "first_name": _s(row, "FRST_NM"),
        "last_name": _s(row, "LAST_NM"),
        "email": email if email != "" else None,
        "phone": _s(row, "PHONE_TX"),
        "preferred_channel": PREF_CHANNELS.get(pref, "email"),
        "marketing_optout": _s(row, "OPTOUT_FLG") == "Y",
        "owner_id": _s(row, "OWNER_UID"),
        "team_code": _s(row, "TEAM_CD"),
        "created_date": _date(row, "CREATE_DT"),
    }


def convert_all(rows):
    out = []
    for row in rows:
        converted = convert_contact(row)
        if converted is not None:
            out.append(converted)
    return out
