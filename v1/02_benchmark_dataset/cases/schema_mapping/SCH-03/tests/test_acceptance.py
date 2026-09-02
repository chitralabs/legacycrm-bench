"""SCH-03 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib

MODERN_KEYS = {
    "opportunity_id", "account_id", "name", "stage", "amount_minor", "currency",
    "close_date", "owner_id", "team_code", "lost_reason", "created_date",
    "updated_date", "migration_flags",
}


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def legacy_row(**over):
    row = {"OPP_ID": "O00000001", "ACCT_ID": "A00000001", "OPP_NM": "Fleet Renewal",
           "STAT_CD": "P", "STAGE_PCT": "10", "AMT": "1234.56", "CURR_CD": "",
           "CLOSE_DT": "00000000", "OWNER_UID": "U0000002", "TEAM_CD": "T01",
           "LOST_RSN": "", "CREATE_DT": "20260101", "UPD_DT": "20260102",
           "DEL_FLG": "N"}
    row.update(over)
    return row


def test_soft_deleted_row_returns_none(mod):
    assert mod.convert_opportunity(legacy_row(DEL_FLG="Y")) is None


def test_output_has_exactly_the_modern_keys(mod):
    out = mod.convert_opportunity(legacy_row())
    assert set(out.keys()) == MODERN_KEYS


def test_stage_pct_not_leaked_and_no_legacy_keys(mod):
    out = mod.convert_opportunity(legacy_row())
    for legacy_key in ("STAT_CD", "STAGE_PCT", "AMT", "CURR_CD", "DEL_FLG", "stage_pct"):
        assert legacy_key not in out


def test_consistent_stage_maps_without_flags(mod):
    out = mod.convert_opportunity(legacy_row(STAT_CD="P", STAGE_PCT="10"))
    assert out["stage"] == "prospecting"
    assert out["migration_flags"] == []


def test_all_status_codes_map_to_enum(mod):
    expected = {"P": ("prospecting", "10"), "Q": ("qualified", "25"),
                "N": ("negotiation", "60"), "W": ("closed_won", "100"),
                "L": ("closed_lost", "0")}
    for code, (stage, pct) in expected.items():
        out = mod.convert_opportunity(legacy_row(STAT_CD=code, STAGE_PCT=pct))
        assert out["stage"] == stage, code
        assert out["migration_flags"] == [], code


def test_mismatched_stage_pct_still_maps_from_stat_cd(mod):
    out = mod.convert_opportunity(legacy_row(STAT_CD="Q", STAGE_PCT="60"))
    assert out["stage"] == "qualified"  # not "negotiation": STAT_CD is trusted
    assert "stage_pct_mismatch" in out["migration_flags"]


def test_blank_stage_pct_coerces_to_zero(mod):
    # L canonical pct is 0, so blank (coerced 0) is consistent; P (canonical 10) is not.
    lost = mod.convert_opportunity(legacy_row(STAT_CD="L", STAGE_PCT="", LOST_RSN="CM"))
    assert lost["migration_flags"] == []
    prospecting = mod.convert_opportunity(legacy_row(STAT_CD="P", STAGE_PCT=""))
    assert prospecting["migration_flags"] == ["stage_pct_mismatch"]


def test_amount_minor_units_usd_default(mod):
    out = mod.convert_opportunity(legacy_row(AMT="1234.56", CURR_CD=""))
    assert out["currency"] == "USD"
    assert out["amount_minor"] == 123456
    assert isinstance(out["amount_minor"], int)


def test_amount_minor_units_jpy_exponent_zero(mod):
    out = mod.convert_opportunity(legacy_row(AMT="5000", CURR_CD="JPY"))
    assert out["currency"] == "JPY"
    assert out["amount_minor"] == 5000


def test_half_up_rounding_jpy(mod):
    out = mod.convert_opportunity(legacy_row(AMT="1234.50", CURR_CD="JPY"))
    assert out["amount_minor"] == 1235


def test_half_up_rounding_usd(mod):
    out = mod.convert_opportunity(legacy_row(AMT="10.005", CURR_CD="USD"))
    assert out["amount_minor"] == 1001


def test_blank_amount_is_zero_minor_units(mod):
    assert mod.convert_opportunity(legacy_row(AMT=""))["amount_minor"] == 0


def test_close_date_sentinel_and_iso(mod):
    assert mod.convert_opportunity(legacy_row(CLOSE_DT="00000000"))["close_date"] is None
    out = mod.convert_opportunity(legacy_row(CLOSE_DT="20260315"))
    assert out["close_date"] == "2026-03-15"


def test_lost_reason_blank_is_none_and_code_verbatim(mod):
    assert mod.convert_opportunity(legacy_row(LOST_RSN=""))["lost_reason"] is None
    out = mod.convert_opportunity(legacy_row(STAT_CD="L", STAGE_PCT="0", LOST_RSN="CM"))
    assert out["lost_reason"] == "CM"


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
# --- Tests added 2026-09-01 after mutation triage (mutant_triage.md #19) ---

def test_opportunity_name_verbatim(mod):
    # name is a verbatim copy of OPP_NM; no prior test asserted its value.
    assert mod.convert_opportunity(legacy_row())["name"] == "Fleet Renewal"
