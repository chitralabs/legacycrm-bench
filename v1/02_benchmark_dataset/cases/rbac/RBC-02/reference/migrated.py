"""RBC-02 reference solution: Meridian CRM permission check migrated to Python.

Preserves SYSTEM_OVERVIEW.md §5 semantics: deny-by-default (missing (role, object, action)
row means NONE), scope evaluation (ALL/TEAM/OWN/NONE), ADMIN scope override, and the DELETE
row-level rule (record must have DEL_FLG currently 'N'; blank counts as 'N' per §1).
"""


def _s(d, key):
    v = d.get(key, "")
    return "" if v is None else str(v)


def can(user, action, object, record, role_rows):
    role = _s(user, "ROLE_ID")
    row = None
    for r in role_rows:
        if r.get("role_id") == role and r.get("object") == object and r.get("action") == action:
            row = r
            break
    if row is None:
        return False  # deny by default: missing row means NONE

    scope = row.get("scope", "NONE")
    if role == "ADMIN":
        scope = "ALL"  # ADMIN bypasses scope, never the row requirement

    if scope == "NONE":
        scope_ok = False
    elif scope == "ALL":
        scope_ok = True
    elif scope == "TEAM":
        scope_ok = _s(user, "TEAM_CD") == _s(record, "TEAM_CD")
    elif scope == "OWN":
        scope_ok = _s(record, "OWNER_UID") == _s(user, "USR_ID")
    else:
        scope_ok = False  # unknown scope value: deny

    if not scope_ok:
        return False

    if action == "DELETE":
        del_flg = _s(record, "DEL_FLG") or "N"  # blank boolean means 'N' (§1)
        if del_flg != "N":
            return False

    return True
