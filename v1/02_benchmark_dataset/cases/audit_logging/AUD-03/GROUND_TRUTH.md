# AUD-03 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/legacy_schema.sql` (AUD_EVENT definition), `legacy/aud_event_sample.csv`, and the audit
semantics in `legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §8). No LLM output was used to
produce expectations. Derivations:

1. EVT_TS is `VARCHAR2(14)` `YYYYMMDDHH24MISS` (schema comment + §8). Slicing
   `20260415103000` as YYYY=2026, MM=04, DD=15, HH=10, MI=30, SS=00 gives ISO-8601
   `2026-04-15T10:30:00` (target-spec format `YYYY-MM-DDTHH:MM:SS`, pure re-slicing).
2. Boundary timestamps by the same slicing: `19991231235959` → `1999-12-31T23:59:59`;
   `20260101000000` → `2026-01-01T00:00:00` (HH24 means 00–23, so midnight is `00`).
3. Field mapping is the target-spec table (evt_id/ts/code/user_id/entity/entity_id/old_val/
   new_val ← EVT_ID/EVT_TS/EVT_CD/USR_ID/ENT_NAME/ENT_ID/OLD_VAL/NEW_VAL); the expected dict
   is the hand-transcribed image of the fixture row. Exactly eight keys.
4. OLD_VAL/NEW_VAL are verbatim strings (§8 "OLD_VAL/NEW_VAL as strings"); empty stays empty
   (no None-ification — legacy empty string is a value).
5. EVT_ID is `NUMBER(12)` → modern `evt_id` is `int`; `"0009"` parses to 9.
6. §8/excerpt: ascending EVT_ID is the canonical event order. Input [10, 2, 31, 4] must land
   in the store as [2, 4, 10, 31] — numeric, not lexicographic (lexicographic would give
   "10" < "2" < "31" < "4", i.e. [10, 2, 31, 4] order unchanged; the test's 31-vs-4 pair
   separates the two).
7. The 10-row sample file fed in reversed order must produce ascending EVT_IDs 1..10 (its
   EVT_IDs are 1–10 by construction of the excerpt) and a store of length 10.
8. Idempotent re-migration (target-spec rule 2, preserving §8 append-only integrity):
   migrating the same 3 rows into the same store twice leaves exactly 3 events, and migrate
   returns the same store object it was given.
9. Overlapping batches: {1,2} then {2,3} → evt_ids [1, 2, 3]; the duplicate 2 is skipped, the
   new 3 is appended after the existing events (append-only: existing rows never move).
10. `append` is the sole mutator and must work (grow the store by one, at the end).
11. §8: "Audit rows are append-only; migrations must preserve append-only behavior" → the
    store class must expose no update/delete/remove/pop/clear/replace/__setitem__/__delitem__
    surface. Negative security expectation of this case.
12. Defensive copies (target-spec rule 3, the modern reading of append-only): clearing the
    list returned by events(), or mutating a returned event dict, must not change the store
    ("TAMPERED" never sticks; original NEW_VAL "W" survives).
13. Security/scan expectation: no network/subprocess imports (as in the VAL-01 exemplar).
