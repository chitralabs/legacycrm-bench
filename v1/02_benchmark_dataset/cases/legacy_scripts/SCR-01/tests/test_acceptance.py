"""SCR-01 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def order(**over):
    rec = {"ORD_ID": "O00000001", "ACCT_ID": "A00000001", "STAT_CD": "E",
           "ORD_DT": "20260810", "DISC_PCT": "0", "TOT_AMT": "0", "DEL_FLG": "N"}
    rec.update(over)
    return rec


def line(no, qty, prc, **over):
    rec = {"ORD_ID": "O00000001", "LINE_NO": no, "PROD_ID": "P0000001",
           "QTY": qty, "UNIT_PRC": prc, "EXT_AMT": "0", "DEL_FLG": "N"}
    rec.update(over)
    return rec


def test_extended_amounts_recomputed_per_line(mod):
    _, lines, _ = mod.recompute(order(), [line(1, "3", "19.99"), line(2, "2", "5.25")])
    assert lines[0]["EXT_AMT"] == 59.97
    assert lines[1]["EXT_AMT"] == 10.50


def test_total_is_sum_of_live_lines_with_audit_on_change(mod):
    new_order, _, audits = mod.recompute(
        order(TOT_AMT="0"), [line(1, "3", "19.99"), line(2, "2", "5.25")])
    assert new_order["TOT_AMT"] == 70.47
    assert audits == [("ORD_RETOTAL", "O00000001")]


def test_discount_applied_then_rounded_half_up_to_cents(mod):
    new_order, _, _ = mod.recompute(order(DISC_PCT="15"), [line(1, "3", "19.99")])
    assert new_order["TOT_AMT"] == 50.97  # 59.97 * 0.85 = 50.9745 -> 50.97


def test_exact_half_cent_rounds_up(mod):
    new_order, _, _ = mod.recompute(order(DISC_PCT="50"), [line(1, "1", "10.01")])
    assert new_order["TOT_AMT"] == 5.01  # 5.005 rounds half-up, not half-even


def test_no_audit_when_total_numerically_unchanged(mod):
    new_order, lines, audits = mod.recompute(
        order(TOT_AMT="10.5"), [line(1, "2", "5.25", EXT_AMT="999")])
    assert audits == []
    assert new_order["TOT_AMT"] == 10.5
    assert lines[0]["EXT_AMT"] == 10.50  # stale EXT_AMT still corrected


def test_soft_deleted_line_excluded_and_untouched(mod):
    new_order, lines, _ = mod.recompute(
        order(), [line(1, "1", "10.00"), line(2, "5", "100", EXT_AMT="500", DEL_FLG="Y")])
    assert new_order["TOT_AMT"] == 10.00
    assert lines[1]["EXT_AMT"] == "500"


def test_cancelled_order_left_untouched(mod):
    o = order(STAT_CD="X", TOT_AMT="123.00")
    lns = [line(1, "3", "19.99", EXT_AMT="1.00")]
    new_order, new_lines, audits = mod.recompute(o, lns)
    assert new_order["TOT_AMT"] == "123.00"
    assert new_lines[0]["EXT_AMT"] == "1.00"
    assert audits == []


def test_soft_deleted_order_left_untouched(mod):
    new_order, _, audits = mod.recompute(
        order(DEL_FLG="Y", TOT_AMT="9.99"), [line(1, "2", "2.00")])
    assert new_order["TOT_AMT"] == "9.99"
    assert audits == []


def test_empty_qty_and_blank_discount_coerce_to_zero(mod):
    new_order, lines, _ = mod.recompute(
        order(DISC_PCT=""), [line(1, "", "9.99"), line(2, "1", "4.00")])
    assert lines[0]["EXT_AMT"] == 0.0
    assert new_order["TOT_AMT"] == 4.00


def test_line_order_and_count_preserved(mod):
    _, lines, _ = mod.recompute(
        order(), [line(2, "1", "1.00"), line(1, "1", "2.00"), line(3, "0", "0", DEL_FLG="Y")])
    assert [l["LINE_NO"] for l in lines] == [2, 1, 3]


def test_inputs_not_mutated(mod):
    o = order(TOT_AMT="0")
    lns = [line(1, "3", "19.99")]
    o_snap, l_snap = dict(o), [dict(l) for l in lns]
    mod.recompute(o, lns)
    assert o == o_snap
    assert lns == l_snap


def test_no_other_audit_codes_emitted(mod):
    _, _, audits = mod.recompute(order(DISC_PCT="15", TOT_AMT="0"),
                                 [line(1, "3", "19.99")])
    assert [a[0] for a in audits] == ["ORD_RETOTAL"]


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
