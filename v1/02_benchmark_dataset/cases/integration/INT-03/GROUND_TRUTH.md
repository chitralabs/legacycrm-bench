# INT-03 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/marketing_sync_endpoint.ini`, the CONT_MASTER column meanings in
`legacy/cont_master_columns.csv`, and the conventions in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §1/§6). The header, column order, separator, and quoting style are
fixed by target_spec.md (the modernization contract for the csv payload). No LLM output
was used to produce expectations. Derivations:

1. Header: fixed by target_spec.md as `CONT_ID,EMAIL_TX,FRST_NM,LAST_NM,PREF_CH`; an
   empty contact list therefore yields exactly that line plus the trailing `\n`.
2. Basic row: values copied verbatim from the fixture contact in column order →
   `K00000001,dana.vail@example.test,Dana,Vail,E`; full payload is header + "\n" +
   row + "\n" (rows joined with `\n`, single trailing newline).
3. Opt-out exclusion: data dictionary — OPTOUT_FLG `Y = excluded from all marketing
   communications`. "All" means the contact contributes nothing: the tests assert its
   CONT_ID, EMAIL_TX, FRST_NM, and LAST_NM are absent from the entire payload string
   (privacy negative expectations; distinctive values K00000009 / optout@example.test /
   Opal / Utter appear nowhere else in the fixtures).
4. Soft-delete exclusion: §1 — `DEL_FLG='Y'` rows are excluded from all reads unless
   stated; nothing here states otherwise, so K00000042 / ghost@example.test never appear.
5. A contact that is both opted out and soft-deleted is excluded for either reason →
   payload is header-only.
6. Blank OPTOUT_FLG: §1 — blank CHAR(1) boolean means `N`, so the contact IS included
   (a migration treating blank as opted-out would silently drop marketable contacts).
7. Blank PREF_CH → `E`: data dictionary meaning "E=email;P=phone;M=mail;blank=E".
   Non-blank codes (P) pass through verbatim.
8. Quoting (target_spec rule 4, RFC-4180 style): `Vail, Jr.` contains a comma →
   `"Vail, Jr."`; `Dana "Dee"` contains quotes → quotes doubled inside an enclosing
   pair: `"Dana ""Dee"""`. Both expected rows were composed by hand from those rules.
9. Order: rows appear in input order (target_spec rule 2); fixture ids are deliberately
   not sorted (K00000003, K00000001, K00000002) so a sorting implementation fails.
10. Trailing newline: exactly one `\n` terminates the payload (target_spec rule 5);
    the test also rejects a doubled newline.
