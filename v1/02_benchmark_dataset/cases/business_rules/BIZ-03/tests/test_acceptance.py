"""BIZ-03 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def order(**over):
    row = {"ORD_ID": "D00000001", "ACCT_ID": "A00000001", "ORD_DT": "20260501",
           "STAT_CD": "I", "CURR_CD": "", "DISC_PCT": 0, "TOT_AMT": "100.00",
           "OWNER_UID": "U0000001", "DEL_FLG": "N"}
    row.update(over)
    return row


def line(line_no=1, qty=1, unit_prc="10.01", ext_amt="", del_flg="N"):
    return {"ORD_ID": "D00000001", "LINE_NO": line_no, "PROD_ID": "P00000001",
            "QTY": qty, "UNIT_PRC": unit_prc, "EXT_AMT": ext_amt, "DEL_FLG": del_flg}


# --- transition_invoiced: ORD-003 + workflow I->X actions -------------------------


def test_invoiced_cancel_moves_to_x(mod):
    updated, _, _ = mod.transition_invoiced(order(), "X")
    assert updated["STAT_CD"] == "X"


def test_invoiced_cancel_emits_ord_canc_inv_audit(mod):
    _, audits, _ = mod.transition_invoiced(order(), "X")
    assert audits == ["ORD_CANC_INV"]


def test_invoiced_cancel_emits_credit_note_notify(mod):
    _, _, notifies = mod.transition_invoiced(order(), "X")
    assert notifies == ["credit_note"]


def test_invoiced_stay_invoiced_is_vacuous(mod):
    updated, audits, notifies = mod.transition_invoiced(order(), "I")
    assert updated["STAT_CD"] == "I" and audits == [] and notifies == []


def test_invoiced_to_approved_raises_e5003(mod):
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.transition_invoiced(order(), "A")
    assert exc.value.code == "E5003"


def test_invoiced_to_entered_raises_e5003(mod):
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.transition_invoiced(order(), "E")
    assert exc.value.code == "E5003"


def test_invoiced_to_shipped_raises_e5003(mod):
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.transition_invoiced(order(), "S")
    assert exc.value.code == "E5003"


def test_violation_preserves_legacy_message(mod):
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.transition_invoiced(order(), "S")
    assert exc.value.message == "Invoiced order can only be cancelled"


def test_non_invoiced_order_is_a_value_error(mod):
    with pytest.raises(ValueError):
        mod.transition_invoiced(order(STAT_CD="A"), "X")


# --- recompute_total: frozen invoiced totals + legacy recompute -------------------


def test_invoiced_total_frozen_despite_line_change(mod):
    # Negative: line now says 5 x 10.01 but the invoiced header must not move.
    updated, _, audits = mod.recompute_total(order(STAT_CD="I", TOT_AMT="100.00"),
                                             [line(qty=5)])
    assert updated["TOT_AMT"] == "100.00"
    assert audits == []


def test_invoiced_lines_left_untouched(mod):
    _, lines_out, _ = mod.recompute_total(order(STAT_CD="I"),
                                          [line(qty=5, ext_amt="10.01")])
    assert lines_out[0]["EXT_AMT"] == "10.01"


def test_cancelled_order_skipped_entirely(mod):
    updated, _, audits = mod.recompute_total(order(STAT_CD="X", TOT_AMT="42.00"),
                                             [line(qty=3)])
    assert updated["TOT_AMT"] == "42.00" and audits == []


def test_entered_order_recomputed_with_half_up_discount(mod):
    # 1 x 10.01 = 10.01; 50% discount -> 5.005 -> half-up -> 5.01; total changed.
    updated, lines_out, audits = mod.recompute_total(
        order(STAT_CD="E", DISC_PCT=50, TOT_AMT="0"), [line()])
    assert lines_out[0]["EXT_AMT"] == 10.01
    assert updated["TOT_AMT"] == 5.01
    assert audits == ["ORD_RETOTAL"]


def test_no_audit_when_total_already_correct(mod):
    # Negative: 2 x 10.00 = 20.00, no discount, stored TOT_AMT already 20.00.
    _, _, audits = mod.recompute_total(
        order(STAT_CD="A", DISC_PCT=0, TOT_AMT="20.00"),
        [line(qty=2, unit_prc="10.00")])
    assert audits == []


def test_soft_deleted_lines_excluded_from_total(mod):
    updated, _, _ = mod.recompute_total(
        order(STAT_CD="A", DISC_PCT=0, TOT_AMT="0"),
        [line(line_no=1, qty=2, unit_prc="10.00"),
         line(line_no=2, qty=100, unit_prc="99.00", del_flg="Y")])
    assert updated["TOT_AMT"] == 20.0


def test_blank_qty_and_disc_pct_coerce_to_zero(mod):
    updated, lines_out, _ = mod.recompute_total(
        order(STAT_CD="E", DISC_PCT="", TOT_AMT="0"),
        [line(qty="", unit_prc="10.00")])
    assert lines_out[0]["EXT_AMT"] == 0.0
    assert updated["TOT_AMT"] == 0.0


def test_inputs_not_mutated(mod):
    o = order(STAT_CD="E", DISC_PCT=50, TOT_AMT="0")
    ls = [line()]
    snap_o, snap_ls = dict(o), [dict(l) for l in ls]
    mod.recompute_total(o, ls)
    mod.transition_invoiced(order(), "X")
    assert o == snap_o and ls == snap_ls
