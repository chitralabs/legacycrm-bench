"""BIZ-03 reference solution: invoiced-order rule preservation.

Combines ORD-003 (E5003: invoiced order may only stay I or move to X), the
order_fulfilment I->X actions (ORD_CANC_INV audit + credit_note notify), and the
order_totals recompute with invoiced totals frozen (modernization per target_spec).
Half-up cent rounding is done on decimals, mirroring the legacy engine.
"""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


class BusinessRuleViolation(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _s(record, field):
    v = record.get(field, "")
    return "" if v is None else str(v)


def _d(value):
    if value is None or value == "":
        return Decimal(0)
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return Decimal(0)


def _cents(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def transition_invoiced(order, new_status):
    if _s(order, "STAT_CD") != "I":
        raise ValueError("transition_invoiced requires an invoiced order")
    if new_status == "I":
        return dict(order), [], []
    if new_status == "X":
        updated = dict(order)
        updated["STAT_CD"] = "X"
        return updated, ["ORD_CANC_INV"], ["credit_note"]
    raise BusinessRuleViolation("E5003", "Invoiced order can only be cancelled")


def recompute_total(order, lines):
    stat = _s(order, "STAT_CD")
    if stat in ("I", "X"):  # invoiced totals frozen; cancelled orders skipped
        return dict(order), [dict(line) for line in lines], []
    new_lines = []
    total = Decimal(0)
    for line in lines:
        new_line = dict(line)
        if _s(line, "DEL_FLG") != "Y":  # live lines only (blank means 'N')
            ext = _cents(_d(line.get("QTY")) * _d(line.get("UNIT_PRC")))
            new_line["EXT_AMT"] = float(ext)
            total += ext
        new_lines.append(new_line)
    discounted = _cents(total * (100 - _d(order.get("DISC_PCT"))) / 100)
    updated = dict(order)
    audits = []
    if _d(order.get("TOT_AMT")) != discounted:
        updated["TOT_AMT"] = float(discounted)
        audits.append("ORD_RETOTAL")
    else:
        updated["TOT_AMT"] = float(discounted)
    return updated, new_lines, audits
