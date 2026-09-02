"""RBC-01 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


@pytest.fixture(scope="module")
def rows():
    return case_lib.read_csv(case_lib.legacy_root(__file__) / "role_permissions.csv")


def user(uid, role, team):
    return {"USR_ID": uid, "ROLE_ID": role, "TEAM_CD": team}

REP = user("U0000003", "REP", "T01")
MGR = user("U0000002", "MGR", "T01")
SUPP = user("U0000004", "SUPP", "T02")


def rec(owner, team, del_flg="N"):
    return {"OWNER_UID": owner, "TEAM_CD": team, "DEL_FLG": del_flg}


def test_missing_action_row_denies(mod, rows):
    # REP has no (OPP_MASTER, DELETE) row -> deny by default even on own record.
    assert mod.can(REP, "DELETE", "OPP_MASTER", rec("U0000003", "T01"), rows) is False


def test_unknown_role_denies_everywhere(mod, rows):
    guest = user("U0000099", "GUEST", "T01")
    assert mod.can(guest, "READ", "ACCT_MASTER", rec("U0000099", "T01"), rows) is False


def test_all_scope_grants_across_teams(mod, rows):
    # MGR,ACCT_MASTER,READ,ALL: foreign owner and foreign team still allowed.
    assert mod.can(MGR, "READ", "ACCT_MASTER", rec("U0000009", "T09"), rows) is True


def test_team_scope_grants_same_team(mod, rows):
    # REP,ACCT_MASTER,READ,TEAM: record owned by a teammate.
    assert mod.can(REP, "READ", "ACCT_MASTER", rec("U0000002", "T01"), rows) is True


def test_team_scope_denies_other_team(mod, rows):
    assert mod.can(REP, "READ", "ACCT_MASTER", rec("U0000009", "T02"), rows) is False


def test_own_scope_grants_owner(mod, rows):
    # REP,OPP_MASTER,UPDATE,OWN.
    assert mod.can(REP, "UPDATE", "OPP_MASTER", rec("U0000003", "T01"), rows) is True


def test_own_scope_denies_teammate_record(mod, rows):
    # Same team is NOT enough for OWN scope.
    assert mod.can(REP, "UPDATE", "OPP_MASTER", rec("U0000002", "T01"), rows) is False


def test_none_scope_denies_even_owner(mod):
    matrix = [{"role_id": "TEMP", "object": "ACCT_MASTER", "action": "READ", "scope": "NONE"}]
    temp = user("U0000010", "TEMP", "T03")
    assert mod.can(temp, "READ", "ACCT_MASTER", rec("U0000010", "T03"), matrix) is False


def test_action_specificity_read_vs_update(mod, rows):
    # REP,CASE_MASTER,READ,TEAM exists; there is no REP,CASE_MASTER,UPDATE row.
    r = rec("U0000002", "T01")
    assert mod.can(REP, "READ", "CASE_MASTER", r, rows) is True
    assert mod.can(REP, "UPDATE", "CASE_MASTER", r, rows) is False


def test_deny_by_default_export(mod, rows):
    # SUPP has no EXPORT rows at all.
    assert mod.can(SUPP, "EXPORT", "CASE_MASTER", rec("U0000004", "T02"), rows) is False


def test_empty_matrix_denies_everything(mod):
    for action in ("READ", "CREATE", "UPDATE", "DELETE", "EXPORT"):
        assert mod.can(MGR, action, "ACCT_MASTER", rec("U0000002", "T01"), []) is False


def test_returns_strict_bool(mod, rows):
    allowed = mod.can(MGR, "READ", "ACCT_MASTER", rec("U0000009", "T09"), rows)
    denied = mod.can(REP, "READ", "ACCT_MASTER", rec("U0000009", "T02"), rows)
    assert allowed is True and denied is False


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
# --- Tests added 2026-09-01 after mutation triage (mutant_triage.md #11, #12) ---

def test_admin_read_bypasses_scope_on_foreign_record(mod, rows):
    # ADMIN,ACCT_MASTER,READ,ALL exists; ADMIN bypasses scope (SYSTEM_OVERVIEW §5).
    admin = user("U0000001", "ADMIN", "T01")
    assert mod.can(admin, "READ", "ACCT_MASTER", rec("U0000009", "T09"), rows) is True


def test_admin_delete_allowed_on_live_foreign_record(mod, rows):
    # ADMIN,OPP_MASTER,DELETE,ALL exists; live record (DEL_FLG='N') satisfies
    # the DELETE row-level rule, and scope is bypassed for ADMIN.
    admin = user("U0000001", "ADMIN", "T01")
    assert mod.can(admin, "DELETE", "OPP_MASTER", rec("U0000009", "T09", "N"), rows) is True


def test_blank_del_flg_counts_as_live_on_delete(mod, rows):
    # §1: blank CHAR(1) boolean means 'N', so a blank DEL_FLG record is deletable.
    # MGR,OPP_MASTER,DELETE,TEAM exists and the record is same-team.
    assert mod.can(MGR, "DELETE", "OPP_MASTER", rec("U0000003", "T01", del_flg=""), rows) is True
