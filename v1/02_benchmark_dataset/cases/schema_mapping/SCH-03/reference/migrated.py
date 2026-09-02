"""SCH-03 reference solution: OPP_MASTER -> modern `opportunity` mapping.

Collapses the redundant STAT_CD/STAGE_PCT pair into one stage enum (STAT_CD is trusted;
disagreement is flagged, not remapped), converts AMT to integer minor units with a
currency-aware exponent (JPY=0, others=2) using the legacy half-up rounding convention,
and applies the sentinel-date / blank-currency / soft-delete conventions.
"""
from decimal import Decimal, ROUND_HALF_UP

SENTINEL = "00000000"

STAGES = {
    "P": ("prospecting", 10),
    "Q": ("qualified", 25),
    "N": ("negotiation", 60),
    "W": ("closed_won", 100),
    "L": ("closed_lost", 0),
}


def _s(row, col):
    v = row.get(col, "")
    return "" if v is None else str(v)


def _date(row, col):
    v = _s(row, col)
    if v == "" or v == SENTINEL:
        return None
    return f"{v[0:4]}-{v[4:6]}-{v[6:8]}"


def _minor_units(amount, currency):
    text = "" if amount is None else str(amount)
    if text == "":
        text = "0"
    exponent = 0 if currency == "JPY" else 2
    scaled = Decimal(text) * (Decimal(10) ** exponent)
    return int(scaled.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def convert_opportunity(row):
    if _s(row, "DEL_FLG") == "Y":
        return None
    stat = _s(row, "STAT_CD")
    stage, canonical_pct = STAGES[stat]
    pct_text = _s(row, "STAGE_PCT")
    pct = float(pct_text) if pct_text != "" else 0.0
    flags = []
    if pct != canonical_pct:
        flags.append("stage_pct_mismatch")
    currency = _s(row, "CURR_CD") or "USD"
    lost = _s(row, "LOST_RSN")
    return {
        "opportunity_id": _s(row, "OPP_ID"),
        "account_id": _s(row, "ACCT_ID"),
        "name": _s(row, "OPP_NM"),
        "stage": stage,
        "amount_minor": _minor_units(row.get("AMT", ""), currency),
        "currency": currency,
        "close_date": _date(row, "CLOSE_DT"),
        "owner_id": _s(row, "OWNER_UID"),
        "team_code": _s(row, "TEAM_CD"),
        "lost_reason": lost if lost != "" else None,
        "created_date": _date(row, "CREATE_DT"),
        "updated_date": _date(row, "UPD_DT"),
        "migration_flags": flags,
    }
