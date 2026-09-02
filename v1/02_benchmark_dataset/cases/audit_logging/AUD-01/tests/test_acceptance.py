"""AUD-01 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


@pytest.fixture(scope="module")
def legacy_cfg():
    return (case_lib.legacy_root(__file__) / "audit_config.cfg").read_text()


def test_all_five_audited_tables_present(mod, legacy_cfg):
    cols = mod.audited_columns(legacy_cfg)
    assert set(cols) == {"ACCT_MASTER", "OPP_MASTER", "CASE_MASTER", "ORD_HEADER", "USR_MASTER"}


def test_acct_master_audited_set(mod, legacy_cfg):
    assert mod.audited_columns(legacy_cfg)["ACCT_MASTER"] == {"CRED_HOLD", "CRED_LIMIT", "OWNER_UID"}


def test_opp_master_audited_set(mod, legacy_cfg):
    assert mod.audited_columns(legacy_cfg)["OPP_MASTER"] == {"STAT_CD", "AMT", "OWNER_UID"}


def test_case_and_order_audited_sets(mod, legacy_cfg):
    cols = mod.audited_columns(legacy_cfg)
    assert cols["CASE_MASTER"] == {"STAT_CD", "SEV_CD"}
    assert cols["ORD_HEADER"] == {"STAT_CD", "DISC_PCT"}


def test_usr_master_audited_set(mod, legacy_cfg):
    assert mod.audited_columns(legacy_cfg)["USR_MASTER"] == {"ROLE_ID", "ACTIVE_FLG"}


def test_unlisted_column_is_not_audited(mod, legacy_cfg):
    cols = mod.audited_columns(legacy_cfg)
    assert "UPD_DT" not in cols["ACCT_MASTER"]
    assert "OPP_NM" not in cols["OPP_MASTER"]


def test_unlisted_table_is_absent(mod, legacy_cfg):
    cols = mod.audited_columns(legacy_cfg)
    assert "CONT_MASTER" not in cols
    assert "ORD_LINE" not in cols


def test_values_are_sets(mod, legacy_cfg):
    for v in mod.audited_columns(legacy_cfg).values():
        assert isinstance(v, set)


def test_comments_and_blank_lines_ignored(mod):
    text = "# header comment\n\nAUDIT T1 C1\n   \n# AUDIT T9 C9\nAUDIT T1 C2\n"
    assert mod.audited_columns(text) == {"T1": {"C1", "C2"}}


def test_duplicate_declarations_are_idempotent(mod):
    text = "AUDIT T1 C1\nAUDIT T1 C1\nAUDIT T1 C1\n"
    assert mod.audited_columns(text) == {"T1": {"C1"}}


def test_empty_config_yields_empty_dict(mod):
    assert mod.audited_columns("# only comments\n\n") == {}


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
