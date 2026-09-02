# INT-02 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/dw_export.crms` and the LAYOUT rows in `legacy/export_acct_layout.csv` under the
CRMScript builtin semantics in `legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §1/§4/§6).
No LLM output was used to produce expectations. Derivations:

1. Record length: LAYOUT widths are 10+40+3+15+1+8 = 77; the legacy expression
   concatenates exactly those six fields with no separator or terminator (CHR(10) is
   appended by the batching loop, not the record builder) → 77 chars, no trailing "\n".
2. Field offsets: LAYOUT POSITION is 1-based, so 0-based Python slices are
   ACCT_ID [0:10], ACCT_NM [10:50], REGION_CD [50:53], ANN_REV [53:68],
   CRED_HOLD [68], CREATE_DT [69:77].
3. `FIXED(s, w)` = left-align, space-pad, truncate to w (§4). "A00000001" is 9 chars →
   "A00000001 " (one trailing space). "Acme Industrial Group" is 21 chars → itself +
   19 spaces in the 40-wide name field.
4. Truncation test: a 48-char name whose 40th char is 'Y' and chars 41.. spell
   "OVERFLOW" must yield exactly the first 40 chars in [10:50]; "OVERFLOW" appearing
   anywhere in the record would mean truncation happened at the wrong width (negative
   expectation).
5. Blank REGION_CD: FIXED("", 3) = three spaces.
6. ANN_REV cents: expression is `ZPAD(NVL(ANN_REV,0) * 100, 15)`. For "2500000.50":
   2500000.50 × 100 = 250000050 exactly; zero-padded to 15 → "000000250000050".
7. Blank ANN_REV: NVL → 0 → 0 cents → "000000000000000".
8. Half-up rounding: ZPAD is defined (§4) as "round half-up to integer". For "999.995":
   999.995 × 100 = 99999.5 exactly in decimal arithmetic → half-up → 100000 →
   "000000000100000". (A float implementation computes 999.995*100 ≈ 99999.49999999999
   and rounds to 99999 — this test detects that divergence; the decimal derivation is
   the documented one.)
9. CRED_HOLD: expression `NVL(CRED_HOLD, 'N')` plus layout note "blank written as N" →
   blank/missing → "N"; "Y" preserved.
10. CREATE_DT: layout "YYYYMMDD; 00000000 if null" and §1's date-sentinel convention →
    "20190215" verbatim; blank/missing → "00000000".
11. Whole-record test is the character-by-character concatenation of derivations 3, 5–6,
    9–10 for the base row:
    "A00000001 " + "Acme Industrial Group"+19 spaces + "NAM" + "000000250000050" + "Y" + "20190215".

12. (added 2026-09-01 after mutation triage) Record width on the blank-date path: LAYOUT
    widths sum to 77 (derivation 1) regardless of which value fills the CREATE_DT field;
    a blank CREATE_DT is written as the 8-char sentinel "00000000" (derivation 10), so the
    record is 69 + 8 = 77 chars. Closes the gap where the width test used a non-blank date
    and the sentinel test sliced only [69:77] (surviving mutant: INT-02 migrated.py
    node 13, SENTINEL_DATE '00000000' -> '00000000_X', which yields a 79-char record).
