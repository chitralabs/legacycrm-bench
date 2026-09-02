"""CFG-01 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import json

import pytest
import case_lib

EXPECTED_KEYS = {
    "ACCT_MASTER.ACCT_TYP", "CONT_MASTER.PREF_CH", "OPP_MASTER.STAT_CD",
    "OPP_MASTER.LOST_RSN", "CASE_MASTER.SEV_CD", "CASE_MASTER.STAT_CD",
    "ORD_HEADER.STAT_CD", "ACT_LOG.ACT_TYP",
}


@pytest.fixture(scope="module")
def enums():
    path = case_lib.solution_file(__file__, "enums.json")
    return json.loads(path.read_text())


def test_top_level_has_exactly_the_eight_code_tables(enums):
    assert isinstance(enums, dict)
    assert set(enums.keys()) == EXPECTED_KEYS


def test_account_type_map(enums):
    assert enums["ACCT_MASTER.ACCT_TYP"] == {
        "C": "Customer", "P": "Prospect", "R": "Partner", "X": "Inactive"}


def test_pref_channel_map_excludes_blank_default(enums):
    assert enums["CONT_MASTER.PREF_CH"] == {"E": "email", "P": "phone", "M": "mail"}
    assert "blank" not in enums["CONT_MASTER.PREF_CH"]


def test_opportunity_status_labels_exact_with_annotations_stripped(enums):
    assert enums["OPP_MASTER.STAT_CD"] == {
        "P": "Prospecting", "Q": "Qualified", "N": "Negotiation",
        "W": "Closed-Won", "L": "Closed-Lost"}


def test_lost_reason_map_preserves_label_spacing(enums):
    assert enums["OPP_MASTER.LOST_RSN"] == {
        "PR": "price", "CM": "competitor", "NB": "no budget", "TM": "timing", "OT": "other"}


def test_severity_map_strips_response_time_annotations(enums):
    assert enums["CASE_MASTER.SEV_CD"] == {
        "1": "Critical", "2": "High", "3": "Normal", "4": "Low"}


def test_case_status_map_preserves_hyphenated_label(enums):
    assert enums["CASE_MASTER.STAT_CD"] == {
        "N": "New", "A": "Assigned", "P": "Pending-Customer", "R": "Resolved", "X": "Closed"}


def test_order_status_map(enums):
    assert enums["ORD_HEADER.STAT_CD"] == {
        "E": "Entered", "A": "Approved", "S": "Shipped", "I": "Invoiced", "X": "Cancelled"}


def test_activity_type_map(enums):
    assert enums["ACT_LOG.ACT_TYP"] == {
        "C": "Call", "E": "Email", "M": "Meeting", "K": "Task"}


def test_convention_columns_not_hallucinated_as_enums(enums):
    for excluded in ("ACCT_MASTER.CURR_CD", "ACCT_MASTER.CRED_HOLD",
                     "CONT_MASTER.OPTOUT_FLG", "ALL.DEL_FLG", "ALL.*_DT"):
        assert excluded not in enums


def test_no_blank_codes_anywhere(enums):
    for table, mapping in enums.items():
        assert "" not in mapping, table
        assert "blank" not in mapping, table


def test_all_labels_are_nonempty_strings(enums):
    for table, mapping in enums.items():
        for code, label in mapping.items():
            assert isinstance(label, str) and label.strip() != "", (table, code)
            assert "(" not in label, (table, code)  # annotations must be stripped
