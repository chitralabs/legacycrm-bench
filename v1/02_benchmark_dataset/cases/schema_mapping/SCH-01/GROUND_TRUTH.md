# SCH-01 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/acct_master.sql`, `legacy/data_dictionary_excerpt.csv`, and the legacy conventions in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §1). No LLM output was used. Derivations:

1. Soft delete: `DEL_FLG='Y'` rows are logically deleted and "excluded from all reads unless
   stated" → `convert_account` returns `None`. `DEL_FLG='N'` (or blank ≠ 'Y') rows convert.
2. Date sentinel: dates are `VARCHAR2(8)` `YYYYMMDD`, `00000000` means NULL →
   `CREATE_DT='20240115'` → `created_date='2024-01-15'`; `UPD_DT='00000000'` →
   `updated_date=None`. ISO form is positional: chars 1-4 year, 5-6 month, 7-8 day.
3. Booleans: `CHAR(1)` in {Y,N}, blank means N (§1) and data dictionary: "N/blank=clear" →
   `CRED_HOLD='Y'` → `True`; `'N'` and `''` → `False`.
4. Currency default: `CURR_CD` blank means USD (§1 and data dictionary row) →
   `CURR_CD=''` → `currency='USD'`; `CURR_CD='EUR'` stays `'EUR'`.
5. Numbers: `ANN_REV NUMBER(15,2)` string `'2500000.00'` → float `2500000.0`. Empty string in
   numeric context coerces to 0 (legacy convention) → blank `ANN_REV`/`CRED_LIMIT` → `0.0`.
6. Key rename: the mapping table in `target_spec.md` fixes the 13 modern keys; presence of any
   legacy key (e.g. `ACCT_ID`, `DEL_FLG`) in the output is a mapping failure (negative
   expectation).
7. Verbatim strings: `ACCT_ID`, `ACCT_NM`, `ACCT_TYP`, `SIC_CD`, `REGION_CD`, `OWNER_UID`,
   `TEAM_CD` are copied unchanged (no code translation is defined for SCH-01).

8. (added 2026-09-01 after mutation triage) Verbatim value assertions for `owner_id` and
   `sic_code`: derivation 7 already establishes that `OWNER_UID` and `SIC_CD` are copied
   unchanged (no code translation defined for SCH-01), so the fixture row's
   `OWNER_UID='U0000001'` → `owner_id == "U0000001"` and `SIC_CD='3714'` →
   `sic_code == "3714"`. Closes the gap that `test_verbatim_string_fields` asserted other
   fields but not these two (surviving mutant: SCH-01 migrated.py node 172,
   `_s(row,'OWNER_UID')` -> `_s(row,'OWNER_UID_X')`, which blanks owner_id).
