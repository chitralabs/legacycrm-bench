"""RBC-03 reference solution: policy-document-driven permission check.

Reads policy.json (generated 1:1 from role_permissions.csv) from this module's own directory
and enforces SYSTEM_OVERVIEW.md §5/§1 semantics: deny-by-default, ALL/TEAM/OWN/NONE scopes,
ADMIN scope override without row bypass, DELETE requires DEL_FLG currently 'N'.
"""
import json
from pathlib import Path

_POLICY = None


def load_policy():
    global _POLICY
    if _POLICY is None:
        _POLICY = json.loads((Path(__file__).resolve().parent / "policy.json").read_text())
    return _POLICY


def _s(d, key):
    v = d.get(key, "")
    return "" if v is None else str(v)


def can(user, action, object, record):
    policy = load_policy()
    role = _s(user, "ROLE_ID")
    grant = None
    for g in policy["grants"]:
        if g["role"] == role and g["object"] == object and g["action"] == action:
            grant = g
            break
    if grant is None:
        return False  # policy default: deny

    scope = grant["scope"]
    if role == policy.get("admin_role", "ADMIN"):
        scope = "ALL"

    if scope == "ALL":
        scope_ok = True
    elif scope == "TEAM":
        scope_ok = _s(user, "TEAM_CD") == _s(record, "TEAM_CD")
    elif scope == "OWN":
        scope_ok = _s(record, "OWNER_UID") == _s(user, "USR_ID")
    else:  # NONE or unknown
        scope_ok = False

    if not scope_ok:
        return False

    if action == "DELETE" and policy.get("delete_requires_live_record", True):
        if (_s(record, "DEL_FLG") or "N") != "N":
            return False

    return True
