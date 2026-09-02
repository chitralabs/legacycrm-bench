"""SCR-01 reference solution: order_totals.crms migrated to a per-order recompute service.

Preserves legacy semantics (SYSTEM_OVERVIEW.md §4 + order_totals.crms): NVL empty->0
coercion, half-up rounding to cents via exact decimal arithmetic, soft-deleted lines
skipped, cancelled/soft-deleted orders untouched, ORD_RETOTAL audit only on a numeric
change of TOT_AMT.
"""
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


def _d(value):
    """NVL(x, 0) with legacy empty-string coercion, as an exact Decimal."""
    if value is None or value == "":
        return Decimal(0)
    try:
        return Decimal(str(value))
    except ArithmeticError:
        return Decimal(0)
    except ValueError:
        return Decimal(0)


def recompute(order, lines):
    new_order = dict(order)
    new_lines = [dict(l) for l in lines]

    # Outer loop guard: WHERE DEL_FLG = 'N' AND STAT_CD <> 'X'
    if str(order.get("DEL_FLG", "N")) == "Y" or str(order.get("STAT_CD", "")) == "X":
        return new_order, new_lines, []

    total = Decimal(0)
    for line in new_lines:
        if str(line.get("DEL_FLG", "N")) == "Y":
            continue  # inner loop: WHERE DEL_FLG = 'N'
        ext = (_d(line.get("QTY")) * _d(line.get("UNIT_PRC"))).quantize(
            _CENT, rounding=ROUND_HALF_UP)
        line["EXT_AMT"] = float(ext)
        total += ext

    disc = _d(order.get("DISC_PCT"))
    discounted = (total * (Decimal(100) - disc) / Decimal(100)).quantize(
        _CENT, rounding=ROUND_HALF_UP)

    audits = []
    if _d(order.get("TOT_AMT")) != discounted:  # IF ord.TOT_AMT <> discounted
        audits.append(("ORD_RETOTAL", str(order.get("ORD_ID", ""))))
    new_order["TOT_AMT"] = float(discounted)
    return new_order, new_lines, audits
