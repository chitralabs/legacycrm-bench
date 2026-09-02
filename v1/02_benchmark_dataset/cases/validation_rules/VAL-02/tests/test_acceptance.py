"""VAL-02 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib

TODAY = "20260901"


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def codes(errors):
    return [e["code"] for e in errors]


def ok_record(**over):
    rec = {"ACCT_ID": "A00000001", "ACCT_NM": "Acme Industrial", "ACCT_TYP": "C",
           "SIC_CD": "3714", "REGION_CD": "NAM", "ANN_REV": 1000, "CURR_CD": "",
           "OWNER_UID": "U0000001", "TEAM_CD": "T01", "CRED_LIMIT": 50000,
           "CRED_HOLD": "N", "CREATE_DT": "20240115", "UPD_DT": "20260101",
           "DEL_FLG": "N"}
    rec.update(over)
    return rec


def test_compliant_insert_returns_empty(mod):
    assert mod.validate(ok_record(), None, "INSERT", TODAY) == []


def test_one_char_name_blocked(mod):
    errs = mod.validate(ok_record(ACCT_NM="A"), None, "INSERT", TODAY)
    assert codes(errs) == ["E1001"]
    assert errs[0]["severity"] == "BLOCK"


def test_invalid_account_type_blocked(mod):
    assert codes(mod.validate(ok_record(ACCT_TYP="Z"), None, "INSERT", TODAY)) == ["E1002"]


def test_negative_revenue_blocked(mod):
    assert codes(mod.validate(ok_record(ANN_REV=-1), None, "INSERT", TODAY)) == ["E1003"]


def test_blank_revenue_passes_via_nvl(mod):
    assert mod.validate(ok_record(ANN_REV=""), None, "INSERT", TODAY) == []


def test_release_credit_hold_with_zero_limit_blocked_on_update(mod):
    old = ok_record(CRED_HOLD="Y", CRED_LIMIT=0)
    new = ok_record(CRED_HOLD="N", CRED_LIMIT=0)
    errs = mod.validate(new, old, "UPDATE", TODAY)
    assert codes(errs) == ["E1004"]
    assert mod.is_blocked(errs) is True


def test_release_credit_hold_with_positive_limit_allowed(mod):
    old = ok_record(CRED_HOLD="Y", CRED_LIMIT=5000)
    new = ok_record(CRED_HOLD="N", CRED_LIMIT=5000)
    assert mod.validate(new, old, "UPDATE", TODAY) == []


def test_release_rule_not_fired_on_insert(mod):
    rec = ok_record(CRED_HOLD="N", CRED_LIMIT=0)
    assert "E1004" not in codes(mod.validate(rec, None, "INSERT", TODAY))


def test_keeping_hold_with_zero_limit_allowed(mod):
    old = ok_record(CRED_HOLD="Y", CRED_LIMIT=0)
    new = ok_record(CRED_HOLD="Y", CRED_LIMIT=0)
    assert mod.validate(new, old, "UPDATE", TODAY) == []


def test_blank_credit_limit_coerces_to_zero_on_release(mod):
    old = ok_record(CRED_HOLD="Y", CRED_LIMIT="")
    new = ok_record(CRED_HOLD="N", CRED_LIMIT="")
    assert codes(mod.validate(new, old, "UPDATE", TODAY)) == ["E1004"]


def test_two_char_region_is_warn_only(mod):
    errs = mod.validate(ok_record(REGION_CD="NA"), None, "INSERT", TODAY)
    assert codes(errs) == ["E1005"]
    assert errs[0]["severity"] == "WARN"
    assert mod.is_blocked(errs) is False


def test_multiple_failures_collected_in_file_order(mod):
    rec = ok_record(ACCT_NM="A", ACCT_TYP="Z")
    assert codes(mod.validate(rec, None, "INSERT", TODAY)) == ["E1001", "E1002"]


def test_empty_record_fails_expected_rules_only(mod):
    errs = mod.validate({}, None, "INSERT", TODAY)
    assert codes(errs) == ["E1001", "E1002", "E1005"]
    assert mod.is_blocked(errs) is True


def test_error_dicts_carry_legacy_messages(mod):
    old = ok_record(CRED_HOLD="Y", CRED_LIMIT=0)
    new = ok_record(CRED_HOLD="N", CRED_LIMIT=0)
    errs = mod.validate(new, old, "UPDATE", TODAY)
    assert errs[0]["message"] == "Cannot release credit hold with zero credit limit"


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
# --- Tests added 2026-09-01 after mutation triage (mutant_triage.md #23) ---

def test_remaining_legal_account_types_pass(mod):
    # ACC-002 accepts exactly C/P/R/X; only 'C' (and invalid 'Z') were tested.
    for t in ("P", "R", "X"):
        assert mod.validate(ok_record(ACCT_TYP=t), None, "INSERT", TODAY) == []
