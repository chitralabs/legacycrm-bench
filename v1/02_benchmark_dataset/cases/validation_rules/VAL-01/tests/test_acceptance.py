"""VAL-01 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib

TODAY = "20260901"


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def codes(errors):
    return [e["code"] for e in errors]


def ok_insert(**over):
    rec = {"OPP_ID": "O00000001", "ACCT_ID": "A00000001", "OPP_NM": "Test Deal",
           "STAT_CD": "P", "STAGE_PCT": 10, "AMT": 100, "CURR_CD": "",
           "CLOSE_DT": "00000000", "OWNER_UID": "U0000002", "TEAM_CD": "T01",
           "LOST_RSN": "", "CREATE_DT": "20260101", "UPD_DT": "20260101", "DEL_FLG": "N"}
    rec.update(over)
    return rec


def test_compliant_insert_returns_empty(mod):
    assert mod.validate(ok_insert(), None, "INSERT", TODAY) == []


def test_won_without_amount_collects_both_failures_in_order(mod):
    rec = ok_insert(STAT_CD="W", STAGE_PCT=100, AMT=0, CLOSE_DT="00000000")
    assert codes(mod.validate(rec, None, "INSERT", TODAY)) == ["E3002", "E3004"]


def test_empty_string_amount_coerces_to_zero(mod):
    rec = ok_insert(STAT_CD="W", STAGE_PCT=100, AMT="", CLOSE_DT="00000000")
    assert codes(mod.validate(rec, None, "INSERT", TODAY)) == ["E3002", "E3004"]


def test_negative_amount_blocked(mod):
    errs = mod.validate(ok_insert(AMT=-5), None, "INSERT", TODAY)
    assert codes(errs) == ["E3001"]
    assert errs[0]["severity"] == "BLOCK"
    assert mod.is_blocked(errs) is True


def test_lost_without_reason_blocked(mod):
    rec = ok_insert(STAT_CD="L", STAGE_PCT=0, LOST_RSN="")
    assert codes(mod.validate(rec, None, "INSERT", TODAY)) == ["E3003"]


def test_reopen_won_rejected_on_update(mod):
    old = ok_insert(STAT_CD="W", STAGE_PCT=100, AMT=500, CLOSE_DT="20260401")
    new = dict(old, STAT_CD="Q", STAGE_PCT=25)
    assert codes(mod.validate(new, old, "UPDATE", TODAY)) == ["E3005"]


def test_update_only_rule_not_fired_on_insert(mod):
    rec = ok_insert(STAT_CD="Q", STAGE_PCT=25)
    assert "E3005" not in codes(mod.validate(rec, None, "INSERT", TODAY))


def test_stage_percent_mismatch_blocked(mod):
    rec = ok_insert(STAT_CD="P", STAGE_PCT=25)
    assert codes(mod.validate(rec, None, "INSERT", TODAY)) == ["E3006"]


def test_past_close_date_is_warn_only(mod):
    rec = ok_insert(CLOSE_DT="20250101")
    errs = mod.validate(rec, None, "INSERT", TODAY)
    assert codes(errs) == ["E3007"]
    assert errs[0]["severity"] == "WARN"
    assert mod.is_blocked(errs) is False


def test_warn_rule_not_fired_on_update(mod):
    old = ok_insert()
    new = ok_insert(CLOSE_DT="20250101")
    assert "E3007" not in codes(mod.validate(new, old, "UPDATE", TODAY))


def test_sentinel_close_date_passes_warn_rule_via_equality(mod):
    rec = ok_insert(CLOSE_DT="00000000")
    assert "E3007" not in codes(mod.validate(rec, None, "INSERT", TODAY))


def test_missing_keys_behave_as_empty_strings(mod):
    errs = mod.validate({}, None, "INSERT", TODAY)
    assert codes(errs) == ["E3006", "E3007"]
    assert mod.is_blocked(errs) is True  # E3006 is BLOCK


def test_error_dicts_carry_legacy_messages(mod):
    errs = mod.validate(ok_insert(AMT=-1), None, "INSERT", TODAY)
    assert errs[0]["message"] == "Amount negative"


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
# --- Tests added 2026-09-01 after mutation triage (mutant_triage.md #20) ---

def test_future_close_date_passes_warn_rule(mod):
    # OPP-007: CLOSE_DT >= TODAY() lexicographic; '20261231' >= '20260901' -> pass.
    assert mod.validate(ok_insert(CLOSE_DT="20261231"), None, "INSERT", TODAY) == []


def test_close_date_equal_to_today_passes_warn_rule(mod):
    # OPP-007 boundary: >= is inclusive, so CLOSE_DT == TODAY passes.
    assert mod.validate(ok_insert(CLOSE_DT=TODAY), None, "INSERT", TODAY) == []
