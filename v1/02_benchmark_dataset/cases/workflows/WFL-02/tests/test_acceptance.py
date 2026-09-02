"""WFL-02 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def case(**over):
    rec = {"CASE_ID": "C00000001", "ACCT_ID": "A00000001", "SUBJ_TX": "Printer on fire",
           "STAT_CD": "N", "SEV_CD": "2", "OWNER_UID": "U0000002", "ESC_FLG": "N",
           "OPEN_DT": "20260820", "RES_DT": "00000000", "DEL_FLG": "N"}
    rec.update(over)
    return rec


def test_assign_with_owner(mod):
    res = mod.fire("N", "assign", case(OWNER_UID="U0000002"))
    assert res["state"] == "A"
    assert res["audits"] == ["CASE_ASSIGN"]
    assert res["notifies"] == []
    assert res["matched"] is True


def test_assign_without_owner_is_nomatch(mod):
    res = mod.fire("N", "assign", case(OWNER_UID=""))
    assert res["state"] == "N"
    assert res["audits"] == ["WF_NOMATCH"]
    assert res["matched"] is False


def test_escalate_new_case_defaults_blank_severity(mod):
    res = mod.fire("N", "auto_escalate", case(SEV_CD="", ESC_FLG="N"))
    assert res["state"] == "A"
    assert res["record"]["ESC_FLG"] == "Y"
    assert res["record"]["SEV_CD"] == "3"
    assert res["audits"] == ["CASE_ESC"]
    assert res["notifies"] == ["escalation"]


def test_escalate_new_case_keeps_explicit_severity(mod):
    res = mod.fire("N", "auto_escalate", case(SEV_CD="1"))
    assert res["record"]["SEV_CD"] == "1"
    assert res["record"]["ESC_FLG"] == "Y"


def test_escalate_assigned_case_is_matched_self_transition(mod):
    res = mod.fire("A", "auto_escalate", case(STAT_CD="A", ESC_FLG="N", SEV_CD=""))
    assert res["state"] == "A"
    assert res["matched"] is True
    assert res["record"]["ESC_FLG"] == "Y"
    assert res["record"]["SEV_CD"] == ""  # A->A row has no SEV_CD set action
    assert res["audits"] == ["CASE_ESC"]
    assert res["notifies"] == ["escalation"]


def test_already_escalated_assigned_case_is_nomatch(mod):
    rec = case(STAT_CD="A", ESC_FLG="Y")
    res = mod.fire("A", "auto_escalate", rec)
    assert res["state"] == "A"
    assert res["matched"] is False
    assert res["audits"] == ["WF_NOMATCH"]
    assert res["notifies"] == []
    assert res["record"] == rec


def test_blank_esc_flag_counts_as_not_escalated(mod):
    res = mod.fire("A", "auto_escalate", case(STAT_CD="A", ESC_FLG=""))
    assert res["matched"] is True
    assert res["record"]["ESC_FLG"] == "Y"


def test_await_customer(mod):
    res = mod.fire("A", "await_customer", case(STAT_CD="A"))
    assert res["state"] == "P"
    assert res["audits"] == ["CASE_PEND"]


def test_customer_reply_has_no_actions(mod):
    res = mod.fire("P", "customer_reply", case(STAT_CD="P"))
    assert res["state"] == "A"
    assert res["audits"] == []
    assert res["notifies"] == []
    assert res["matched"] is True


def test_resolve_with_resolution_date(mod):
    res = mod.fire("A", "resolve", case(STAT_CD="A", RES_DT="20260810"))
    assert res["state"] == "R"
    assert res["audits"] == ["CASE_RES"]


def test_resolve_with_sentinel_date_is_nomatch(mod):
    res = mod.fire("A", "resolve", case(STAT_CD="A", RES_DT="00000000"))
    assert res["state"] == "A"
    assert res["audits"] == ["WF_NOMATCH"]
    assert res["matched"] is False


def test_close_resolved_case(mod):
    res = mod.fire("R", "close", case(STAT_CD="R", RES_DT="20260810"))
    assert res["state"] == "X"
    assert res["audits"] == ["CASE_CLOSE"]


def test_reopen_clears_resolution_date(mod):
    res = mod.fire("R", "reopen", case(STAT_CD="R", RES_DT="20260810"))
    assert res["state"] == "A"
    assert res["record"]["RES_DT"] == "00000000"
    assert res["audits"] == ["CASE_REOPEN"]


def test_reopened_case_cannot_resolve_without_new_date(mod):
    reopened = mod.fire("R", "reopen", case(STAT_CD="R", RES_DT="20260810"))
    res = mod.fire("A", "resolve", reopened["record"])
    assert res["matched"] is False
    assert res["audits"] == ["WF_NOMATCH"]


def test_closed_state_has_no_transitions(mod):
    res = mod.fire("X", "reopen", case(STAT_CD="X"))
    assert res["state"] == "X"
    assert res["audits"] == ["WF_NOMATCH"]
    assert res["matched"] is False


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
