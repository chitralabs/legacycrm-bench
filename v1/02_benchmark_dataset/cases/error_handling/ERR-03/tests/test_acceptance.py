"""ERR-03 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import re
import pytest
import case_lib

TYPE_URI = "https://meridian-crm.example/problems/validation"


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


@pytest.fixture(scope="module")
def vrl_codes():
    text = (case_lib.legacy_root(__file__) / "validation_rules.vrl").read_text()
    return re.findall(r"ERROR\s+(E\d{4})", text)


def err(code, message="msg", severity="BLOCK"):
    return {"code": code, "message": message, "severity": severity}


def test_empty_input_is_open_document(mod):
    doc = mod.problem_details([])
    assert doc["blocked"] is False
    assert doc["status"] == 200
    assert doc["errors"] == []


def test_single_block_failure(mod):
    doc = mod.problem_details([err("E3001", "Amount negative")])
    assert doc["blocked"] is True
    assert doc["status"] == 422
    assert doc["errors"] == [{"code": "E3001", "message": "Amount negative",
                              "severity": "BLOCK"}]


def test_warn_only_is_not_blocked_but_reported(mod):
    doc = mod.problem_details([err("E3007", "Close date in past", "WARN")])
    assert doc["blocked"] is False
    assert doc["status"] == 200
    assert [e["code"] for e in doc["errors"]] == ["E3007"]
    assert doc["errors"][0]["severity"] == "WARN"


def test_mixed_severities_blocked_and_all_retained(mod):
    doc = mod.problem_details([err("E1005", "Region", "WARN"), err("E1001", "Name")])
    assert doc["blocked"] is True and doc["status"] == 422
    assert [e["code"] for e in doc["errors"]] == ["E1005", "E1001"]
    assert [e["severity"] for e in doc["errors"]] == ["WARN", "BLOCK"]


def test_no_code_is_dropped(mod):
    codes = ["E3002", "E3004", "E3006", "E5001", "E4001"]
    doc = mod.problem_details([err(c) for c in codes])
    assert [e["code"] for e in doc["errors"]] == codes


def test_order_is_preserved_not_sorted(mod):
    # Reverse-sorted input must come back reverse-sorted (re-sorting is a failure).
    codes = ["E5004", "E3002", "E1001"]
    doc = mod.problem_details([err(c) for c in codes])
    assert [e["code"] for e in doc["errors"]] == codes


def test_duplicate_entries_are_retained_verbatim(mod):
    doc = mod.problem_details([err("E3001"), err("E3001")])
    assert [e["code"] for e in doc["errors"]] == ["E3001", "E3001"]


def test_every_legacy_code_is_accepted(mod, vrl_codes):
    assert len(set(vrl_codes)) == 25  # sanity of the excerpt itself
    for code in vrl_codes:
        doc = mod.problem_details([err(code)])
        assert doc["errors"][0]["code"] == code


def test_invented_code_rejected(mod):
    with pytest.raises(ValueError):
        mod.problem_details([err("E9999")])


def test_malformed_code_rejected(mod):
    with pytest.raises(ValueError):
        mod.problem_details([err("X123")])


def test_invented_code_hidden_among_valid_ones_rejected(mod):
    with pytest.raises(ValueError):
        mod.problem_details([err("E3001"), err("E8888"), err("E3002")])


def test_fixed_type_and_title(mod):
    doc = mod.problem_details([err("E2001")])
    assert doc["type"] == TYPE_URI
    assert doc["title"] == "Legacy validation failed"


def test_document_shape_keys_exact(mod):
    doc = mod.problem_details([err("E2002", severity="WARN")])
    assert set(doc.keys()) == {"type", "title", "status", "blocked", "errors"}
    assert set(doc["errors"][0].keys()) == {"code", "message", "severity"}


def test_module_contains_no_invented_ecodes(mod, vrl_codes):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    in_module = set(re.findall(r"E\d{4}", src))
    assert in_module <= set(vrl_codes), f"invented codes in module: {in_module - set(vrl_codes)}"
