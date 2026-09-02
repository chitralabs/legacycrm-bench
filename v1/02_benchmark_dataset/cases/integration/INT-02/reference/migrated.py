"""INT-02 reference solution: EXPORT_ACCT fixed-width record builder.

Mirrors dw_export.crms under CRMScript builtin semantics (SYSTEM_OVERVIEW.md §4):
FIXED = left-align/space-pad/truncate; ZPAD = round half-up to integer, zero-pad;
NVL defaults; record = 10+40+3+15+1+8 = 77 chars, no terminator.
"""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

SENTINEL_DATE = "00000000"


def _s(row, field):
    v = row.get(field, "")
    return "" if v is None else str(v)


def _fixed(s, w):
    return s[:w].ljust(w)


def _zpad_cents(value, w):
    if value is None or value == "":
        value = "0"
    try:
        cents = (Decimal(str(value)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        cents = Decimal(0)
    return str(cents).rjust(w, "0")


def format_account(row):
    cred = _s(row, "CRED_HOLD") or "N"
    create_dt = _s(row, "CREATE_DT") or SENTINEL_DATE
    return (
        _fixed(_s(row, "ACCT_ID"), 10)
        + _fixed(_s(row, "ACCT_NM"), 40)
        + _fixed(_s(row, "REGION_CD"), 3)
        + _zpad_cents(row.get("ANN_REV", ""), 15)
        + cred
        + create_dt
    )
