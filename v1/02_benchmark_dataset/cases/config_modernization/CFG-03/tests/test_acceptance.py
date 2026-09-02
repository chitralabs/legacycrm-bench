"""CFG-03 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md.

The XML in legacy/ is the case's own artifact; tests parse it with stdlib xml.etree to
build the completeness/hallucination oracle, and the hand counts in GROUND_TRUTH.md pin
that parse (workflow/state/transition counts are asserted literally).
"""
import json
import xml.etree.ElementTree as ET

import pytest
import case_lib


@pytest.fixture(scope="module")
def wf_json():
    path = case_lib.solution_file(__file__, "workflows.json")
    return json.loads(path.read_text())


@pytest.fixture(scope="module")
def wf_xml():
    return ET.parse(case_lib.legacy_root(__file__) / "workflows.xml").getroot()


def by_name(wf_json, name):
    matches = [w for w in wf_json["workflows"] if w["name"] == name]
    assert len(matches) == 1
    return matches[0]


def transition(wf, frm, to, event):
    matches = [t for t in wf["transitions"]
               if (t["from"], t["to"], t["event"]) == (frm, to, event)]
    assert len(matches) == 1
    return matches[0]


def test_three_workflows_in_document_order(wf_json):
    assert [w["name"] for w in wf_json["workflows"]] == [
        "opportunity_pipeline", "case_lifecycle", "order_fulfilment"]


def test_entities_and_state_fields(wf_json):
    expected = {"opportunity_pipeline": "OPP_MASTER", "case_lifecycle": "CASE_MASTER",
                "order_fulfilment": "ORD_HEADER"}
    for name, entity in expected.items():
        wf = by_name(wf_json, name)
        assert wf["entity"] == entity
        assert wf["state_field"] == "STAT_CD"


def test_states_in_document_order(wf_json):
    assert [s["code"] for s in by_name(wf_json, "opportunity_pipeline")["states"]] == \
        ["P", "Q", "N", "W", "L"]
    assert [s["code"] for s in by_name(wf_json, "case_lifecycle")["states"]] == \
        ["N", "A", "P", "R", "X"]
    assert [s["code"] for s in by_name(wf_json, "order_fulfilment")["states"]] == \
        ["E", "A", "S", "I", "X"]


def test_exactly_one_initial_state_per_workflow(wf_json):
    expected = {"opportunity_pipeline": "P", "case_lifecycle": "N", "order_fulfilment": "E"}
    for name, initial in expected.items():
        wf = by_name(wf_json, name)
        initials = [s["code"] for s in wf["states"] if s["initial"] is True]
        assert initials == [initial]


def test_timers_preserved_only_where_the_xml_has_them(wf_json):
    cl = by_name(wf_json, "case_lifecycle")
    timers = {s["code"]: s["timers"] for s in cl["states"]}
    assert timers["N"] == [{"after_days": 2, "event": "auto_escalate"}]
    assert timers["A"] == [{"after_days": 7, "event": "auto_escalate"}]
    assert timers["P"] == [] and timers["R"] == [] and timers["X"] == []
    for name in ("opportunity_pipeline", "order_fulfilment"):
        assert all(s["timers"] == [] for s in by_name(wf_json, name)["states"])


def test_hand_counted_transition_totals(wf_json):
    assert len(by_name(wf_json, "opportunity_pipeline")["transitions"]) == 6
    assert len(by_name(wf_json, "case_lifecycle")["transitions"]) == 8
    assert len(by_name(wf_json, "order_fulfilment")["transitions"]) == 6


def test_opportunity_transitions_in_document_order(wf_json):
    wf = by_name(wf_json, "opportunity_pipeline")
    assert [(t["from"], t["to"], t["event"]) for t in wf["transitions"]] == [
        ("P", "Q", "qualify"), ("Q", "N", "advance"), ("N", "W", "close_won"),
        ("P", "L", "close_lost"), ("Q", "L", "close_lost"), ("N", "L", "close_lost")]


def test_guards_kept_verbatim_after_entity_decoding(wf_json):
    opp = by_name(wf_json, "opportunity_pipeline")
    assert transition(opp, "P", "Q", "qualify")["guard"] == "NVL(AMT,0) > 0"
    assert transition(opp, "N", "W", "close_won")["guard"] == "CLOSE_DT <> '00000000'"
    ord_wf = by_name(wf_json, "order_fulfilment")
    assert transition(ord_wf, "A", "X", "cancel")["guard"] == \
        "LOOKUP(ACCT_MASTER, ACCT_ID, ACCT_ID, CRED_HOLD) <> 'Y'"


def test_unguarded_transitions_have_null_guard(wf_json):
    opp = by_name(wf_json, "opportunity_pipeline")
    assert transition(opp, "Q", "N", "advance")["guard"] is None
    cl = by_name(wf_json, "case_lifecycle")
    assert transition(cl, "P", "A", "customer_reply")["guard"] is None


def test_invoiced_cancel_actions_in_order(wf_json):
    ord_wf = by_name(wf_json, "order_fulfilment")
    assert transition(ord_wf, "I", "X", "cancel")["actions"] == [
        {"type": "audit", "code": "ORD_CANC_INV"},
        {"type": "notify", "template": "credit_note"}]


def test_set_actions_keep_values_verbatim_including_expr(wf_json):
    cl = by_name(wf_json, "case_lifecycle")
    assert transition(cl, "N", "A", "auto_escalate")["actions"] == [
        {"type": "set", "field": "ESC_FLG", "value": "Y"},
        {"type": "set", "field": "SEV_CD", "value": "=NVL(SEV_CD,'3')"},
        {"type": "audit", "code": "CASE_ESC"},
        {"type": "notify", "template": "escalation"}]
    assert transition(cl, "R", "A", "reopen")["actions"] == [
        {"type": "set", "field": "RES_DT", "value": "00000000"},
        {"type": "audit", "code": "CASE_REOPEN"}]


def test_actionless_transition_has_empty_actions_list(wf_json):
    cl = by_name(wf_json, "case_lifecycle")
    assert transition(cl, "P", "A", "customer_reply")["actions"] == []


def xml_transition_set(wf_xml):
    tuples = set()
    for wf in wf_xml.findall("workflow"):
        for t in wf.findall("transition"):
            tuples.add((wf.get("name"), t.get("from"), t.get("to"), t.get("event")))
    return tuples


def json_transition_set(wf_json):
    tuples = set()
    for wf in wf_json["workflows"]:
        for t in wf["transitions"]:
            tuples.add((wf["name"], t["from"], t["to"], t["event"]))
    return tuples


def test_completeness_no_xml_transition_missing(wf_json, wf_xml):
    xml_set = xml_transition_set(wf_xml)
    assert len(xml_set) == 20  # hand count pins the parse
    assert xml_set - json_transition_set(wf_json) == set()


def test_hallucination_no_invented_transitions(wf_json, wf_xml):
    assert json_transition_set(wf_json) - xml_transition_set(wf_xml) == set()


def test_no_invented_states(wf_json, wf_xml):
    for wf in wf_xml.findall("workflow"):
        xml_states = {s.get("code") for s in wf.find("states").findall("state")}
        json_states = {s["code"] for s in by_name(wf_json, wf.get("name"))["states"]}
        assert json_states == xml_states, wf.get("name")
