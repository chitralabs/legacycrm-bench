"""SCR-03 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib

TODAY = "20260901"


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def case(case_id="C00000001", **over):
    rec = {"CASE_ID": case_id, "ACCT_ID": "A00000001", "STAT_CD": "N", "SEV_CD": "3",
           "ESC_FLG": "N", "OPEN_DT": "20260901", "RES_DT": "00000000", "DEL_FLG": "N"}
    rec.update(over)
    return rec


def event(case_id):
    return {"workflow": "case_lifecycle", "entity_id": case_id, "event": "auto_escalate"}


def test_new_case_two_days_old_escalates(mod):
    assert mod.escalate([case(OPEN_DT="20260830")], TODAY) == [event("C00000001")]


def test_new_case_one_day_old_does_not_escalate(mod):
    assert mod.escalate([case(OPEN_DT="20260831")], TODAY) == []


def test_new_case_opened_today_does_not_escalate(mod):
    assert mod.escalate([case(OPEN_DT="20260901")], TODAY) == []


def test_new_case_much_older_still_escalates(mod):
    assert mod.escalate([case(OPEN_DT="20260820")], TODAY) == [event("C00000001")]


def test_assigned_case_seven_days_old_escalates(mod):
    cases = [case(STAT_CD="A", ESC_FLG="N", OPEN_DT="20260825")]
    assert mod.escalate(cases, TODAY) == [event("C00000001")]


def test_assigned_case_six_days_old_does_not_escalate(mod):
    assert mod.escalate([case(STAT_CD="A", OPEN_DT="20260826")], TODAY) == []


def test_already_escalated_assigned_case_is_skipped(mod):
    cases = [case(STAT_CD="A", ESC_FLG="Y", OPEN_DT="20260825")]
    assert mod.escalate(cases, TODAY) == []


def test_blank_esc_flag_counts_as_not_escalated(mod):
    cases = [case(STAT_CD="A", ESC_FLG="", OPEN_DT="20260825")]
    assert mod.escalate(cases, TODAY) == [event("C00000001")]


def test_new_case_rule_ignores_esc_flag(mod):
    cases = [case(STAT_CD="N", ESC_FLG="Y", OPEN_DT="20260820")]
    assert mod.escalate(cases, TODAY) == [event("C00000001")]


def test_sentinel_open_date_never_overdue(mod):
    cases = [case(OPEN_DT="00000000"),
             case(case_id="C00000002", STAT_CD="A", OPEN_DT="00000000")]
    assert mod.escalate(cases, TODAY) == []


def test_missing_open_date_never_overdue(mod):
    assert mod.escalate([case(OPEN_DT="")], TODAY) == []


def test_future_open_date_never_overdue(mod):
    assert mod.escalate([case(OPEN_DT="20260905")], TODAY) == []


def test_soft_deleted_case_is_skipped(mod):
    assert mod.escalate([case(OPEN_DT="20260820", DEL_FLG="Y")], TODAY) == []


def test_other_statuses_never_escalate(mod):
    cases = [case(case_id="C00000001", STAT_CD="P", OPEN_DT="20260801"),
             case(case_id="C00000002", STAT_CD="R", OPEN_DT="20260801"),
             case(case_id="C00000003", STAT_CD="X", OPEN_DT="20260801")]
    assert mod.escalate(cases, TODAY) == []


def test_datediff_is_calendar_aware_across_month_boundary(mod):
    # 2026 is not a leap year: Feb 27 -> Mar 1 is exactly 2 days.
    assert mod.escalate([case(OPEN_DT="20260227")], "20260301") == [event("C00000001")]


def test_events_ordered_by_case_id_ascending(mod):
    cases = [case(case_id="C00000009", STAT_CD="N", OPEN_DT="20260820"),
             case(case_id="C00000001", STAT_CD="A", ESC_FLG="N", OPEN_DT="20260801")]
    assert mod.escalate(cases, TODAY) == [event("C00000001"), event("C00000009")]


def test_at_most_one_event_per_case(mod):
    events = mod.escalate([case(OPEN_DT="20260801")], TODAY)
    assert len(events) == 1


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
