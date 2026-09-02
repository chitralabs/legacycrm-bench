# SCH-03 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/opp_master.sql`, `legacy/data_dictionary_excerpt.csv`, and the conventions in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §1 and the ZPAD half-up convention of
§4). No LLM output was used. Derivations:

1. Stage enum: data dictionary STAT_CD meaning string fixes P=Prospecting(10%),
   Q=Qualified(25%), N=Negotiation(60%), W=Closed-Won(100%), L=Closed-Lost(0%). target_spec
   fixes the modern enum spelling: prospecting/qualified/negotiation/closed_won/closed_lost
   and the canonical percents 10/25/60/100/0.
2. Trust STAT_CD: STAGE_PCT is documented in the schema comment as a "legacy duplicate of
   STAT_CD". A row with STAT_CD='Q', STAGE_PCT='60' therefore maps to stage "qualified"
   (NOT "negotiation"), with migration_flags == ["stage_pct_mismatch"] because 60 != 25.
3. Consistent row: STAT_CD='P', STAGE_PCT='10' → 10 == canonical 10 → flags [].
4. Blank STAGE_PCT coerces to 0 (empty string in numeric context is 0, §1/§2 convention):
   STAT_CD='L' + STAGE_PCT='' → 0 == canonical 0 → no mismatch flag; STAT_CD='P' +
   STAGE_PCT='' → 0 != 10 → flagged.
5. Minor units, exponent 2: AMT='1234.56' with blank CURR_CD → currency USD, exponent 2 →
   1234.56 × 100 = 123456 exactly (AMT is NUMBER(15,2), so ×100 of the decimal string is
   exact) → amount_minor == 123456 (int).
6. Minor units, JPY exponent 0: AMT='5000', CURR_CD='JPY' → 5000 × 10^0 = 5000.
7. Half-up rounding (ZPAD convention): AMT='1234.50', CURR_CD='JPY' → 1234.5 rounds half-up
   to 1235. AMT='10.005', CURR_CD='USD' → 1000.5 minor units rounds half-up to 1001.
   (Derived on the decimal string, not binary floats.)
8. Blank AMT → 0 minor units (empty-numeric-is-zero convention).
9. CLOSE_DT sentinel '00000000' → None; '20260315' → '2026-03-15' (§1 date convention).
10. LOST_RSN: two-letter code verbatim ('CM' stays 'CM'); blank → None (modern null).
11. Soft delete: DEL_FLG='Y' → None (§1).
12. Key set: exactly the 13 modern keys of the target_spec table; STAGE_PCT and DEL_FLG and
    every other legacy name absent (negative expectation).

13. (added 2026-09-01 after mutation triage) Verbatim `name`: the target_spec mapping table
    renames OPP_NM to `name` with no transformation defined, so the fixture value
    "Fleet Renewal" is copied unchanged. Closes the gap that tests checked the key set and
    stage/amount/date logic but never the name value (surviving mutant: SCH-03
    migrated.py node 283, `_s(row,'OPP_NM')` -> `_s(row,'OPP_NM_X')`, which blanks it).
