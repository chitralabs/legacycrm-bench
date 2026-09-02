"""RIN-02 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def line(ord_id, line_no, prod="P00000001", del_flg="N", **over):
    row = {"ORD_ID": ord_id, "LINE_NO": line_no, "PROD_ID": prod,
           "QTY": 1, "UNIT_PRC": "10.00", "EXT_AMT": "10.00", "DEL_FLG": del_flg}
    row.update(over)
    return row


def nos(rows):
    return [r["LINE_NO"] for r in rows]


def test_gaps_closed_to_contiguous_from_one(mod):
    out = mod.renumber([line("D00000001", 1), line("D00000001", 3), line("D00000001", 7)])
    assert nos(out) == [1, 2, 3]


def test_relative_order_and_fields_preserved(mod):
    out = mod.renumber([line("D00000001", 2, prod="P00000002"),
                        line("D00000001", 5, prod="P00000005")])
    assert [r["PROD_ID"] for r in out] == ["P00000002", "P00000005"]
    assert out[0]["QTY"] == 1 and out[0]["UNIT_PRC"] == "10.00"


def test_soft_deleted_lines_removed_and_take_no_number(mod):
    # Negative: the deleted line's product must be absent from the output.
    out = mod.renumber([line("D00000001", 1),
                        line("D00000001", 2, prod="P00000099", del_flg="Y"),
                        line("D00000001", 3)])
    assert nos(out) == [1, 2]
    assert all(r["PROD_ID"] != "P00000099" for r in out)


def test_already_contiguous_input_unchanged(mod):
    rows = [line("D00000001", 1), line("D00000001", 2), line("D00000001", 3)]
    assert nos(mod.renumber(rows)) == [1, 2, 3]


def test_idempotent(mod):
    rows = [line("D00000001", 4), line("D00000001", 9, del_flg="Y"),
            line("D00000001", 10), line("D00000002", 2)]
    once = mod.renumber(rows)
    assert mod.renumber(once) == once


def test_numeric_ordering_of_string_line_numbers(mod):
    # NUMBER(4): "2" sorts before "10"; lexicographic order would invert them.
    out = mod.renumber([line("D00000001", "10", prod="P00000010"),
                        line("D00000001", "2", prod="P00000002")])
    assert [r["PROD_ID"] for r in out] == ["P00000002", "P00000010"]
    assert nos(out) == [1, 2]


def test_multiple_orders_each_restart_at_one(mod):
    out = mod.renumber([line("D00000001", 5), line("D00000002", 8),
                        line("D00000001", 9)])
    by_order = {}
    for r in out:
        by_order.setdefault(r["ORD_ID"], []).append(r["LINE_NO"])
    assert by_order == {"D00000001": [1, 2], "D00000002": [1]}


def test_output_grouped_by_ord_id_ascending(mod):
    out = mod.renumber([line("D00000002", 1), line("D00000001", 1),
                        line("D00000002", 2)])
    assert [(r["ORD_ID"], r["LINE_NO"]) for r in out] == \
        [("D00000001", 1), ("D00000002", 1), ("D00000002", 2)]


def test_new_line_numbers_are_ints(mod):
    out = mod.renumber([line("D00000001", "3")])
    assert type(out[0]["LINE_NO"]) is int


def test_input_not_mutated(mod):
    rows = [line("D00000001", 3), line("D00000001", 5, del_flg="Y")]
    snap = [dict(r) for r in rows]
    mod.renumber(rows)
    assert rows == snap


def test_empty_input_returns_empty(mod):
    assert mod.renumber([]) == []


def test_all_deleted_returns_empty(mod):
    out = mod.renumber([line("D00000001", 1, del_flg="Y"),
                        line("D00000001", 2, del_flg="Y")])
    assert out == []
