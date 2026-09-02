"""RBC-03 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md.

The equivalence oracle below implements the documented legacy semantics
(SYSTEM_OVERVIEW.md §5, §1 = legacy/SEMANTICS_EXCERPT.md) directly over the legacy
matrix excerpt; it is hand-written from the spec, not from any solution.
"""
import json
import pytest
import case_lib

ACTIONS = ("READ", "CREATE", "UPDATE", "DELETE", "EXPORT")
OBJECTS = ("ACCT_MASTER", "CONT_MASTER", "OPP_MASTER", "CASE_MASTER", "ORD_HEADER", "AUD_EVENT")

USERS = [
    {"USR_ID": "U0000001", "ROLE_ID": "ADMIN", "TEAM_CD": "T01"},
    {"USR_ID": "U0000002", "ROLE_ID": "MGR", "TEAM_CD": "T01"},
    {"USR_ID": "U0000003", "ROLE_ID": "REP", "TEAM_CD": "T01"},
    {"USR_ID": "U0000004", "ROLE_ID": "SUPP", "TEAM_CD": "T02"},
    {"USR_ID": "U0000005", "ROLE_ID": "AUDIT", "TEAM_CD": "T02"},
    {"USR_ID": "U0000006", "ROLE_ID": "GUEST", "TEAM_CD": "T01"},  # unknown role
]

RECORDS = [
    {"OWNER_UID": "U0000003", "TEAM_CD": "T01", "DEL_FLG": "N"},  # owned by the REP user
    {"OWNER_UID": "U0000002", "TEAM_CD": "T01", "DEL_FLG": "N"},  # teammate-owned
    {"OWNER_UID": "U0000009", "TEAM_CD": "T09", "DEL_FLG": "N"},  # foreign team
    {"OWNER_UID": "U0000003", "TEAM_CD": "T01", "DEL_FLG": "Y"},  # soft-deleted
]


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


@pytest.fixture(scope="module")
def matrix():
    return case_lib.read_csv(case_lib.legacy_root(__file__) / "role_permissions.csv")


@pytest.fixture(scope="module")
def policy():
    return json.loads(case_lib.solution_file(__file__, "policy.json").read_text())


def legacy_can(user, action, obj, record, matrix_rows):
    """Legacy oracle, hand-written from SYSTEM_OVERVIEW.md §5/§1 (see GROUND_TRUTH.md)."""
    role = user.get("ROLE_ID", "")
    row = next((r for r in matrix_rows
                if r["role_id"] == role and r["object"] == obj and r["action"] == action), None)
    if row is None:
        return False  # deny by default
    scope = "ALL" if role == "ADMIN" else row["scope"]
    if scope == "ALL":
        ok = True
    elif scope == "TEAM":
        ok = user.get("TEAM_CD", "") == record.get("TEAM_CD", "")
    elif scope == "OWN":
        ok = record.get("OWNER_UID", "") == user.get("USR_ID", "")
    else:  # NONE
        ok = False
    if ok and action == "DELETE" and (record.get("DEL_FLG", "") or "N") != "N":
        ok = False
    return ok


def all_tuples():
    return [(u, rec, obj, act) for u in USERS for rec in RECORDS
            for obj in OBJECTS for act in ACTIONS]


def test_enumeration_covers_at_least_200_tuples(mod):
    # mod is required so this meta-check cannot pass for a missing solution.
    assert len(all_tuples()) >= 200


def test_full_decision_equivalence_with_legacy_matrix(mod, matrix):
    mismatches = []
    for u, rec, obj, act in all_tuples():
        expected = legacy_can(u, act, obj, rec, matrix)
        got = mod.can(u, act, obj, rec)
        if got is not expected:
            mismatches.append((u["ROLE_ID"], act, obj, rec["OWNER_UID"], rec["DEL_FLG"],
                               "expected", expected, "got", got))
    assert mismatches == []


def test_no_privilege_widening_anywhere(mod, matrix):
    widened = [(u["ROLE_ID"], act, obj, rec["OWNER_UID"], rec["TEAM_CD"], rec["DEL_FLG"])
               for u, rec, obj, act in all_tuples()
               if mod.can(u, act, obj, rec) and not legacy_can(u, act, obj, rec, matrix)]
    assert widened == []


def test_policy_grants_no_triple_absent_from_legacy_matrix(policy, matrix):
    legacy = {(r["role_id"], r["object"], r["action"]): r["scope"] for r in matrix}
    for g in policy["grants"]:
        key = (g["role"], g["object"], g["action"])
        assert key in legacy, f"invented grant {key}"
        assert g["scope"] == legacy[key], f"scope changed for {key}"


def test_policy_contains_every_legacy_row_in_file_order(policy, matrix):
    expected = [(r["role_id"], r["object"], r["action"], r["scope"]) for r in matrix]
    got = [(g["role"], g["object"], g["action"], g["scope"]) for g in policy["grants"]]
    assert got == expected


def test_policy_default_is_deny(policy):
    assert policy["default"] == "deny"
    assert policy["version"] == 1


def test_admin_denied_without_grant(mod):
    admin = USERS[0]
    live = {"OWNER_UID": "U0000001", "TEAM_CD": "T01", "DEL_FLG": "N"}
    # No ADMIN,OPP_MASTER,EXPORT row exists in the legacy matrix.
    assert mod.can(admin, "EXPORT", "OPP_MASTER", live) is False


def test_admin_delete_blocked_on_soft_deleted_record(mod):
    admin = USERS[0]
    gone = {"OWNER_UID": "U0000009", "TEAM_CD": "T09", "DEL_FLG": "Y"}
    assert mod.can(admin, "DELETE", "ACCT_MASTER", gone) is False


def test_rep_update_own_vs_foreign_opportunity(mod):
    rep = USERS[2]
    assert mod.can(rep, "UPDATE", "OPP_MASTER", RECORDS[0]) is True
    assert mod.can(rep, "UPDATE", "OPP_MASTER", RECORDS[1]) is False


def test_audit_role_reads_but_never_writes_audit_events(mod):
    audit = USERS[4]
    live = {"OWNER_UID": "U0000005", "TEAM_CD": "T02", "DEL_FLG": "N"}
    assert mod.can(audit, "READ", "AUD_EVENT", live) is True
    for act in ("CREATE", "UPDATE", "DELETE", "EXPORT"):
        assert mod.can(audit, act, "AUD_EVENT", live) is False


def test_unknown_role_denied_everywhere(mod):
    guest = USERS[5]
    for obj in OBJECTS:
        for act in ACTIONS:
            assert mod.can(guest, act, obj, RECORDS[0]) is False


def test_no_forbidden_imports_and_no_invented_ecodes(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
    # policy.json roles must all come from the legacy matrix (no invented roles).
    policy = json.loads(case_lib.solution_file(__file__, "policy.json").read_text())
    matrix = case_lib.read_csv(case_lib.legacy_root(__file__) / "role_permissions.csv")
    assert {g["role"] for g in policy["grants"]} <= {r["role_id"] for r in matrix}
