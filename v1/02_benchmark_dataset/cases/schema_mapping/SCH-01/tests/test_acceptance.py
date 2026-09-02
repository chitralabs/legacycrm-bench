"""SCH-01 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib

MODERN_KEYS = {
    "account_id", "name", "account_type", "sic_code", "region", "annual_revenue",
    "currency", "owner_id", "team_code", "credit_limit", "credit_hold",
    "created_date", "updated_date",
}


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def legacy_row(**over):
    row = {"ACCT_ID": "A00000001", "ACCT_NM": "Acme Industrial", "ACCT_TYP": "C",
           "SIC_CD": "3714", "REGION_CD": "NAM", "ANN_REV": "2500000.00",
           "CURR_CD": "", "OWNER_UID": "U0000001", "TEAM_CD": "T01",
           "CRED_LIMIT": "50000.00", "CRED_HOLD": "N", "CREATE_DT": "20240115",
           "UPD_DT": "00000000", "DEL_FLG": "N"}
    row.update(over)
    return row


def test_soft_deleted_row_returns_none(mod):
    assert mod.convert_account(legacy_row(DEL_FLG="Y")) is None


def test_live_row_has_exactly_the_modern_keys(mod):
    out = mod.convert_account(legacy_row())
    assert set(out.keys()) == MODERN_KEYS


def test_no_legacy_keys_leak_into_output(mod):
    out = mod.convert_account(legacy_row())
    for legacy_key in ("ACCT_ID", "ACCT_NM", "CURR_CD", "DEL_FLG", "del_flg"):
        assert legacy_key not in out


def test_date_converted_to_iso(mod):
    out = mod.convert_account(legacy_row(CREATE_DT="20240115"))
    assert out["created_date"] == "2024-01-15"


def test_sentinel_date_becomes_none(mod):
    out = mod.convert_account(legacy_row(UPD_DT="00000000"))
    assert out["updated_date"] is None


def test_credit_hold_y_is_true(mod):
    out = mod.convert_account(legacy_row(CRED_HOLD="Y"))
    assert out["credit_hold"] is True


def test_credit_hold_n_and_blank_are_false(mod):
    assert mod.convert_account(legacy_row(CRED_HOLD="N"))["credit_hold"] is False
    assert mod.convert_account(legacy_row(CRED_HOLD=""))["credit_hold"] is False


def test_blank_currency_defaults_to_usd(mod):
    assert mod.convert_account(legacy_row(CURR_CD=""))["currency"] == "USD"


def test_explicit_currency_preserved(mod):
    assert mod.convert_account(legacy_row(CURR_CD="EUR"))["currency"] == "EUR"


def test_annual_revenue_is_float(mod):
    out = mod.convert_account(legacy_row(ANN_REV="2500000.00"))
    assert isinstance(out["annual_revenue"], float)
    assert out["annual_revenue"] == 2500000.0


def test_blank_numerics_coerce_to_zero(mod):
    out = mod.convert_account(legacy_row(ANN_REV="", CRED_LIMIT=""))
    assert out["annual_revenue"] == 0.0
    assert out["credit_limit"] == 0.0


def test_verbatim_string_fields(mod):
    out = mod.convert_account(legacy_row())
    assert out["account_id"] == "A00000001"
    assert out["name"] == "Acme Industrial"
    assert out["account_type"] == "C"
    assert out["region"] == "NAM"
    assert out["team_code"] == "T01"


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
# --- Tests added 2026-09-01 after mutation triage (mutant_triage.md #15) ---

def test_verbatim_owner_id_and_sic_code(mod):
    # owner_id and sic_code are verbatim copies of OWNER_UID / SIC_CD
    # (GROUND_TRUTH derivation 7); previously unasserted on the value level.
    out = mod.convert_account(legacy_row())
    assert out["owner_id"] == "U0000001"
    assert out["sic_code"] == "3714"
