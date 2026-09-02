"""RBC-02 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
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

ADMIN = user("U0000001", "ADMIN", "T01")
MGR = user("U0000002", "MGR", "T01")


def rec(owner, team, del_flg="N"):
    return {"OWNER_UID": owner, "TEAM_CD": team, "DEL_FLG": del_flg}


def test_admin_delete_bypasses_scope(mod, rows):
    # ADMIN,OPP_MASTER,DELETE,ALL exists; foreign owner and team are irrelevant for ADMIN.
    assert mod.can(ADMIN, "DELETE", "OPP_MASTER", rec("U0000009", "T09"), rows) is True


def test_admin_row_scope_value_is_ignored(mod):
    # Even a (hypothetical) ADMIN row with scope OWN is treated as ALL.
    matrix = [{"role_id": "ADMIN", "object": "ACCT_MASTER", "action": "UPDATE", "scope": "OWN"}]
    assert mod.can(ADMIN, "UPDATE", "ACCT_MASTER", rec("U0000009", "T09"), matrix) is True


def test_admin_without_row_is_denied_no_widening(mod, rows):
    # The matrix has no ADMIN,OPP_MASTER,EXPORT row -> ADMIN is denied (row bypass is a bug).
    assert mod.can(ADMIN, "EXPORT", "OPP_MASTER", rec("U0000001", "T01"), rows) is False


def test_admin_without_delete_row_is_denied(mod, rows):
    # ADMIN has ORD_HEADER READ/UPDATE rows but no DELETE row.
    assert mod.can(ADMIN, "DELETE", "ORD_HEADER", rec("U0000001", "T01"), rows) is False


def test_admin_denied_on_object_with_no_admin_rows(mod, rows):
    # No ADMIN,ORD_LINE,* rows exist at all.
    assert mod.can(ADMIN, "READ", "ORD_LINE", rec("U0000001", "T01"), rows) is False


def test_delete_denied_on_soft_deleted_record_even_for_admin(mod, rows):
    # ADMIN,ACCT_MASTER,DELETE,ALL exists, but DEL_FLG='Y' fails the row-level rule.
    assert mod.can(ADMIN, "DELETE", "ACCT_MASTER", rec("U0000009", "T09", "Y"), rows) is False


def test_delete_allowed_on_live_record(mod, rows):
    assert mod.can(ADMIN, "DELETE", "ACCT_MASTER", rec("U0000009", "T09", "N"), rows) is True


def test_blank_del_flg_counts_as_live(mod, rows):
    # §1: blank CHAR(1) boolean means 'N', so a blank DEL_FLG record is deletable.
    assert mod.can(ADMIN, "DELETE", "CONT_MASTER", rec("U0000009", "T09", ""), rows) is True


def test_non_admin_delete_also_requires_live_record(mod, rows):
    # MGR,OPP_MASTER,DELETE,TEAM: same team but record already soft-deleted.
    assert mod.can(MGR, "DELETE", "OPP_MASTER", rec("U0000003", "T01", "Y"), rows) is False
    assert mod.can(MGR, "DELETE", "OPP_MASTER", rec("U0000003", "T01", "N"), rows) is True


def test_non_admin_delete_still_scope_checked(mod, rows):
    # Live record, but the TEAM scope fails for a foreign team: DEL_FLG='N' does not widen.
    assert mod.can(MGR, "DELETE", "OPP_MASTER", rec("U0000009", "T09", "N"), rows) is False


def test_del_flg_rule_applies_only_to_delete(mod, rows):
    # ADMIN,ACCT_MASTER,UPDATE,ALL: permission decision ignores DEL_FLG for non-DELETE actions.
    assert mod.can(ADMIN, "UPDATE", "ACCT_MASTER", rec("U0000009", "T09", "Y"), rows) is True


def test_admin_all_five_actions_only_where_rows_exist(mod, rows):
    # ACCT_MASTER has all five ADMIN rows; CASE_MASTER lacks CREATE and EXPORT for ADMIN.
    live = rec("U0000009", "T09", "N")
    for action in ("READ", "CREATE", "UPDATE", "DELETE", "EXPORT"):
        assert mod.can(ADMIN, action, "ACCT_MASTER", live, rows) is True
    assert mod.can(ADMIN, "CREATE", "CASE_MASTER", live, rows) is False
    assert mod.can(ADMIN, "EXPORT", "CASE_MASTER", live, rows) is False


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
# --- Tests added 2026-09-01 after mutation triage (mutant_triage.md #13) ---

def test_own_scope_grants_record_owner(mod, rows):
    # REP,OPP_MASTER,UPDATE,OWN exists; OWN grants when OWNER_UID == user id
    # (SYSTEM_OVERVIEW §5). Prior RBC-02 tests never exercised a granting OWN row.
    rep = user("U0000003", "REP", "T01")
    assert mod.can(rep, "UPDATE", "OPP_MASTER", rec("U0000003", "T01"), rows) is True
