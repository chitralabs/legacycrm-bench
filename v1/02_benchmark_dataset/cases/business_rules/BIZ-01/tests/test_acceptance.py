"""BIZ-01 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def acct(**over):
    row = {"ACCT_ID": "A00000001", "ACCT_NM": "Acme Industrial", "ACCT_TYP": "C",
           "CRED_LIMIT": "50000.00", "CRED_HOLD": "Y", "CURR_CD": "",
           "DEL_FLG": "N"}
    row.update(over)
    return row


def test_release_with_positive_limit_clears_hold(mod):
    updated, _ = mod.release_credit_hold(acct())
    assert updated["CRED_HOLD"] == "N"


def test_release_emits_exactly_one_cred_hold_off_audit(mod):
    _, audits = mod.release_credit_hold(acct())
    assert audits == [{"code": "CRED_HOLD_OFF", "entity_id": "A00000001"}]


def test_release_changes_no_other_field(mod):
    original = acct()
    updated, _ = mod.release_credit_hold(original)
    assert {k: v for k, v in updated.items() if k != "CRED_HOLD"} == \
        {k: v for k, v in original.items() if k != "CRED_HOLD"}


def test_zero_limit_raises_e1004(mod):
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.release_credit_hold(acct(CRED_LIMIT="0.00"))
    assert exc.value.code == "E1004"


def test_negative_limit_raises_e1004(mod):
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.release_credit_hold(acct(CRED_LIMIT="-100.00"))
    assert exc.value.code == "E1004"


def test_blank_limit_coerces_to_zero_and_raises(mod):
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.release_credit_hold(acct(CRED_LIMIT=""))
    assert exc.value.code == "E1004"


def test_smallest_positive_limit_allows_release(mod):
    updated, audits = mod.release_credit_hold(acct(CRED_LIMIT="0.01"))
    assert updated["CRED_HOLD"] == "N"
    assert len(audits) == 1


def test_not_on_hold_is_vacuous_no_audit(mod):
    # Negative: the rule only fires on a Y->N transition; no CRED_HOLD_OFF here.
    updated, audits = mod.release_credit_hold(acct(CRED_HOLD="N", CRED_LIMIT="0.00"))
    assert updated["CRED_HOLD"] == "N"
    assert audits == []


def test_blank_hold_means_not_on_hold(mod):
    updated, audits = mod.release_credit_hold(acct(CRED_HOLD="", CRED_LIMIT="0.00"))
    assert updated["CRED_HOLD"] == ""
    assert audits == []


def test_violation_message_preserves_legacy_text(mod):
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.release_credit_hold(acct(CRED_LIMIT="0"))
    assert exc.value.message == "Cannot release credit hold with zero credit limit"


def test_input_not_mutated_on_success_or_failure(mod):
    ok = acct()
    snap_ok = dict(ok)
    mod.release_credit_hold(ok)
    assert ok == snap_ok
    bad = acct(CRED_LIMIT="0.00")
    snap_bad = dict(bad)
    with pytest.raises(mod.BusinessRuleViolation):
        mod.release_credit_hold(bad)
    assert bad == snap_bad
