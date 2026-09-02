"""CFG-02 reference solution: legacy storage-convention utilities.

Modernizes the Meridian CRM 4.2 conventions (SYSTEM_OVERVIEW.md par.1, par.4): YYYYMMDD
dates with the 00000000 sentinel, CHAR(1) Y/N booleans with blank=N, blank currency = USD,
and half-up (ZPAD-convention) conversion of decimal amounts to integer minor units with a
currency-aware exponent (JPY=0, others=2).
"""
from decimal import Decimal, ROUND_HALF_UP

SENTINEL = "00000000"


def to_iso(yyyymmdd):
    if yyyymmdd is None or yyyymmdd == "" or yyyymmdd == SENTINEL:
        return None
    v = str(yyyymmdd)
    return f"{v[0:4]}-{v[4:6]}-{v[6:8]}"


def from_iso(iso):
    if iso is None or iso == "":
        return SENTINEL
    return str(iso).replace("-", "")


def yn(char):
    return char == "Y"


def to_minor_units(amount, currency):
    text = "" if amount is None else str(amount)
    if text == "":
        text = "0"
    curr = currency or "USD"
    exponent = 0 if curr == "JPY" else 2
    scaled = Decimal(text) * (Decimal(10) ** exponent)
    return int(scaled.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
