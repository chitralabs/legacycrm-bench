# CFG-02 Target Specification

Modernize the four cross-cutting legacy storage conventions (`legacy/SEMANTICS_EXCERPT.md`,
`legacy/data_dictionary_excerpt.csv`) into one reusable utility module **`migrated.py`** so
that every future migration converts them the same way.

## Required interface

```python
def to_iso(yyyymmdd: str | None) -> str | None: ...
def from_iso(iso: str | None) -> str: ...
def yn(char: str | None) -> bool: ...
def to_minor_units(amount, currency: str | None) -> int: ...
```

## Required behavior

1. `to_iso`: `"YYYYMMDD"` → `"YYYY-MM-DD"`. The sentinel `"00000000"`, the empty string, and
   `None` all mean "no value" → return `None`.
2. `from_iso`: `"YYYY-MM-DD"` → `"YYYYMMDD"`. `None` (and `""`) → the legacy sentinel
   `"00000000"`. Round-trip property: `from_iso(to_iso(d)) == d` for any valid legacy value
   including the sentinel, and `to_iso(from_iso(s)) == s` for any ISO date or `None`.
3. `yn`: `'Y'` → `True`; `'N'`, blank (`''`), and `None` → `False` (legacy: blank means N).
4. `to_minor_units(amount, currency)`: convert a legacy decimal amount (str, int, or float)
   to an `int` of currency minor units. Blank/`None` currency → `"USD"`. The currency
   exponent is **0 for JPY** and **2 for every other currency in this dataset**. Rounding is
   **half-up** (the documented legacy ZPAD convention), applied on the decimal value (use
   `decimal.Decimal(str(amount))`, not binary-float arithmetic). Blank/`None` amount → `0`.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
