"""WFL-01 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def opp(**over):
    rec = {"OPP_ID": "O00000001", "ACCT_ID": "A00000001", "OPP_NM": "Test Deal",
           "STAT_CD": "P", "STAGE_PCT": "10", "AMT": "1500.00", "CURR_CD": "",
           "CLOSE_DT": "00000000", "LOST_RSN": "", "DEL_FLG": "N"}
    rec.update(over)
    return rec


def test_qualify_fires_with_positive_amount(mod):
    res = mod.fire("P", "qualify", opp(AMT="1500.00"))
    assert res["state"] == "Q"
    assert res["record"]["STAGE_PCT"] == "25"
    assert res["audits"] == ["OPP_QUAL"]
    assert res["notifies"] == []
    assert res["matched"] is True


def test_qualify_guard_blocks_zero_amount(mod):
    rec = opp(AMT="0")
    res = mod.fire("P", "qualify", rec)
    assert res["state"] == "P"
    assert res["audits"] == ["WF_NOMATCH"]
    assert res["matched"] is False
    assert res["record"] == rec


def test_empty_amount_coerces_to_zero_in_guard(mod):
    res = mod.fire("P", "qualify", opp(AMT=""))
    assert res["matched"] is False
    assert res["audits"] == ["WF_NOMATCH"]


def test_advance_has_no_guard_and_no_audit(mod):
    res = mod.fire("Q", "advance", opp(STAT_CD="Q", STAGE_PCT="25", AMT=""))
    assert res["state"] == "N"
    assert res["record"]["STAGE_PCT"] == "60"
    assert res["audits"] == []
    assert res["notifies"] == []
    assert res["matched"] is True


def test_close_won_with_close_date(mod):
    res = mod.fire("N", "close_won", opp(STAT_CD="N", CLOSE_DT="20261015"))
    assert res["state"] == "W"
    assert res["record"]["STAGE_PCT"] == "100"
    assert res["audits"] == ["OPP_WON"]
    assert res["notifies"] == ["won_deal"]


def test_close_won_blocked_by_sentinel_close_date(mod):
    res = mod.fire("N", "close_won", opp(STAT_CD="N", CLOSE_DT="00000000"))
    assert res["state"] == "N"
    assert res["audits"] == ["WF_NOMATCH"]
    assert res["matched"] is False


def test_close_lost_from_prospecting(mod):
    res = mod.fire("P", "close_lost", opp(LOST_RSN="CM"))
    assert res["state"] == "L"
    assert res["record"]["STAGE_PCT"] == "0"
    assert res["audits"] == ["OPP_LOST"]


def test_close_lost_without_reason_is_nomatch(mod):
    res = mod.fire("Q", "close_lost", opp(STAT_CD="Q", LOST_RSN=""))
    assert res["state"] == "Q"
    assert res["audits"] == ["WF_NOMATCH"]
    assert res["matched"] is False


def test_close_lost_from_negotiation(mod):
    res = mod.fire("N", "close_lost", opp(STAT_CD="N", LOST_RSN="PR"))
    assert res["state"] == "L"
    assert res["audits"] == ["OPP_LOST"]


def test_undefined_event_for_state_is_nomatch(mod):
    res = mod.fire("P", "close_won", opp(CLOSE_DT="20261015"))
    assert res["state"] == "P"
    assert res["audits"] == ["WF_NOMATCH"]
    assert res["matched"] is False


def test_terminal_state_has_no_transitions(mod):
    res = mod.fire("W", "qualify", opp(STAT_CD="W", AMT="9999"))
    assert res["state"] == "W"
    assert res["audits"] == ["WF_NOMATCH"]
    assert res["matched"] is False


def test_input_record_is_not_mutated(mod):
    rec = opp(AMT="1500.00")
    snapshot = dict(rec)
    mod.fire("P", "qualify", rec)
    assert rec == snapshot


def test_qualify_emits_no_foreign_audits_or_notifies(mod):
    res = mod.fire("P", "qualify", opp(AMT="1"))
    assert "OPP_LOST" not in res["audits"]
    assert "OPP_WON" not in res["audits"]
    assert res["notifies"] == []


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
# --- Tests added 2026-09-01 after mutation triage (mutant_triage.md #26, #27) ---

def test_close_lost_from_qualified_with_reason(mod):
    # The Q->L close_lost row was previously only exercised with a blocked guard.
    res = mod.fire("Q", "close_lost", opp(STAT_CD="Q", LOST_RSN="CM"))
    assert res["state"] == "L"
    assert res["record"]["STAGE_PCT"] == "0"
    assert res["audits"] == ["OPP_LOST"]
    assert res["matched"] is True
