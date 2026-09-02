"""RIN-02 reference solution: ORD_LINE renumbering.

Restores the legacy composite-key invariant (SYSTEM_OVERVIEW.md §1): after removing
soft-deleted lines, LINE_NO is contiguous from 1 per ORD_ID, preserving relative
(numeric) order. Pure and idempotent.
"""


def _s(row, field):
    v = row.get(field, "")
    return "" if v is None else str(v)


def _is_live(row):
    return _s(row, "DEL_FLG") != "Y"  # blank means 'N'


def _line_no(row):
    v = row.get("LINE_NO", 0)
    if v is None or v == "":
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def renumber(lines):
    live = [row for row in lines if _is_live(row)]
    live.sort(key=lambda row: (_s(row, "ORD_ID"), _line_no(row)))
    out = []
    counters = {}
    for row in live:
        ord_id = _s(row, "ORD_ID")
        counters[ord_id] = counters.get(ord_id, 0) + 1
        new_row = dict(row)
        new_row["LINE_NO"] = counters[ord_id]
        out.append(new_row)
    return out
