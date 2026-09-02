# CFG-02 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from the legacy
conventions in `legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §1 sentinels, §4 ZPAD
half-up rounding) and `legacy/data_dictionary_excerpt.csv`. No LLM output was used.
Derivations:

1. `to_iso("20260901")` → positional split YYYY|MM|DD → `"2026-09-01"`.
2. `to_iso("00000000")` → sentinel means NULL (§1, dictionary `00000000=null`) → `None`;
   blank and `None` also mean "no value" → `None`.
3. `from_iso("2026-09-01")` → strip hyphens → `"20260901"`; `from_iso(None)` → the legacy
   null representation → `"00000000"`.
4. Round trips follow from 1–3: `from_iso(to_iso("20240229")) == "20240229"`;
   `from_iso(to_iso("00000000")) == "00000000"` (None maps back to the sentinel);
   `to_iso(from_iso("2025-12-31")) == "2025-12-31"`; `to_iso(from_iso(None)) is None`.
5. `yn`: booleans are CHAR(1) {Y,N} with blank meaning N (§1) → `yn('Y') is True`;
   `yn('N')`, `yn('')`, `yn(None)` are all `False`. Negative expectation: nothing but 'Y'
   maps to True.
6. `to_minor_units("1234.56", "USD")`: exponent 2 → 1234.56 × 100 = 123456 exactly (amounts
   are NUMBER(15,2), the decimal string times 100 is an integer) → `123456` (int).
7. Blank currency means USD (§1) → `to_minor_units("1234.56", "")` and `(..., None)` also
   → `123456`.
8. JPY exponent 0 → `to_minor_units("5000", "JPY")` → 5000 × 1 = `5000`.
9. Half-up (§4 ZPAD convention): `to_minor_units("1234.5", "JPY")` → 1234.5 → `1235`;
   `to_minor_units("19.995", "USD")` → 1999.5 minor units → `2000`;
   `to_minor_units("10.005", "USD")` → 1000.5 → `1001`. These are computed on the decimal
   string — binary-float ×100 of 19.995 would give 1999.4999... and round to 1999, which is
   why the target_spec mandates Decimal(str(amount)).
10. Blank amount coerces to zero (empty-numeric convention, §1/§2) →
    `to_minor_units("", "USD") == 0` and `to_minor_units(None, "JPY") == 0`.
