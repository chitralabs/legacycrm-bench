# SCH-02 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/cont_master.sql`, `legacy/data_dictionary_excerpt.csv`, and the conventions in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §1). No LLM output was used. Derivations:

1. PREF_CH enum: data dictionary row `E=email;P=phone;M=mail;blank=E` → `'E'`→`"email"`,
   `'P'`→`"phone"`, `'M'`→`"mail"`, and blank/missing → the `E` default → `"email"`.
2. OPTOUT_FLG: `Y=excluded from all marketing communications`; boolean convention is CHAR(1)
   Y/N with blank meaning N → `'Y'`→`True`, `'N'`/blank/missing→`False`.
3. Empty EMAIL_TX → `None` (target_spec modernization of the legacy blank-string convention);
   a non-blank email is copied verbatim.
4. Soft delete: `DEL_FLG='Y'` rows are excluded from all reads → `convert_contact` returns
   `None`; `convert_all` omits them entirely.
5. Order preservation: legacy extracts are ordered by primary key; `convert_all` must preserve
   the given input order of surviving rows. With rows K1 (live), K2 (deleted), K3 (live), the
   output ids are exactly `["K00000001", "K00000003"]` in that order.
6. Date sentinel: `CREATE_DT='20230605'` → `'2023-06-05'`; `'00000000'` → `None` (§1).
7. Key rename: mapping table in target_spec fixes the 11 modern keys; any legacy key present
   in the output is a failure (negative expectation).
8. `convert_all([])` → `[]` (no rows, nothing to emit).

9. (added 2026-09-01 after mutation triage) Verbatim value assertions for `first_name`,
   `last_name`, `phone`, `owner_id`: the target_spec mapping table renames
   FRST_NM/LAST_NM/PHONE_TX/OWNER_UID to these keys with no transformation defined
   (unlike EMAIL_TX's blank→None rule of derivation 3), so the fixture values are copied
   unchanged: "Dana", "Whitfield", "+1-555-0142", "U0000001". Closes the gap that no test
   asserted any of these values (surviving mutants: SCH-02 migrated.py nodes 163/172/181,
   `_s(row,'FRST_NM'|'PHONE_TX'|'OWNER_UID')` -> misspelled key, each blanking its field).
