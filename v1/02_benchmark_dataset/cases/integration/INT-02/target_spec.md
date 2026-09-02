# INT-02 Target Specification

Reimplement the EXPORT_ACCT fixed-width record builder used by the legacy nightly
data-warehouse export (`legacy/dw_export.crms`, layout `legacy/export_acct_layout.csv`,
builtin semantics `legacy/SEMANTICS_EXCERPT.md`) as **one Python module** `migrated.py`.

## Required interface

```python
def format_account(row: dict) -> str: ...
```

`row` is one ACCT_MASTER row as a dict of strings (values may also be numbers for
NUMBER columns); missing keys behave as empty string.

## Required behavior (must match the legacy record byte-for-byte)

The returned record is **exactly 77 characters** (10+40+3+15+1+8), built from the
EXPORT_ACCT layout with the exact expression the legacy script uses:

```
FIXED(ACCT_ID, 10) & FIXED(ACCT_NM, 40) & FIXED(REGION_CD, 3)
  & ZPAD(NVL(ANN_REV, 0) * 100, 15) & NVL(CRED_HOLD, 'N') & CREATE_DT
```

1. `FIXED(s, w)`: left-align, pad with spaces on the right to width w, truncate to w
   when longer (ACCT_NM truncated at 40).
2. `ZPAD(num, 15)`: ANN_REV is converted to **integer cents** (ANN_REV × 100, rounded
   half-up to an integer), rendered right-aligned and zero-padded to 15 digits.
   Blank/missing ANN_REV is 0 via NVL → `000000000000000`. Rounding must be true
   half-up on the decimal value (e.g. 999.995 → 99999.5 cents → 100000), not float
   banker's rounding.
3. CRED_HOLD: blank/missing is written as `N` (NVL default); `Y` preserved.
4. CREATE_DT: the 8-char `YYYYMMDD` string verbatim; blank/missing is written as the
   null sentinel `00000000` (layout: "00000000 if null").
5. No record terminator: the newline is added by the batching layer, not by
   `format_account` (the legacy script appends CHR(10) separately).

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
