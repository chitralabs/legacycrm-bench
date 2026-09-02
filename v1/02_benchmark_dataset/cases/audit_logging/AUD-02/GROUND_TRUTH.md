# AUD-02 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/audit_config.cfg`, `legacy/legacy_schema.sql`, and the audit semantics in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §8). No LLM output was used to produce
expectations. Derivations:

1. §8: "Every UPDATE to an audited column ... writes one row per changed column". CRED_HOLD is
   an audited ACCT_MASTER column (cfg line 2); changing N→Y yields exactly one event with
   OLD_VAL "N", NEW_VAL "Y", ENT_NAME ACCT_MASTER, ENT_ID = the row's ACCT_ID (PK per
   legacy_schema.sql), EVT_TS/USR_ID the injected values, EVT_CD "COL_UPD" (fixed by the
   target spec — EVT_ID/EVT_CD assignment is not specified per-column in §8, so the modern
   code value is a target-spec decision, not a legacy-derived one).
2. Order: audit_config.cfg lists ACCT_MASTER columns as CRED_HOLD, CRED_LIMIT, OWNER_UID
   (lines 2–4). Changing CRED_HOLD and OWNER_UID must emit (N→Y) before (U0000002→U0000005) —
   config file order, per the target spec's canonical-order rule (the cfg file order is the
   only order the legacy artifact defines).
3. Identical old/new images: no changed column → no events (per-changed-column emission).
4. ACCT_NM appears nowhere in the cfg → changing it emits nothing (§8 audits only listed
   columns). Negative expectation.
5. CONT_MASTER has no cfg lines at all → any update emits nothing.
6. §8: "with OLD_VAL/NEW_VAL as strings" → numeric 50000/75000 must be stringified to
   "50000"/"75000". Change detection also happens on the stringified values (target spec
   rule 2), so int 50000 vs str "50000" is *not* a change.
7. Missing key / None stringify to "" (legacy uninitialized-value convention: empty string;
   target spec rule 2) → old STAT_CD None → OLD_VAL "".
8. Event field names are exactly the AUD_EVENT columns minus EVT_ID (EVT_ID is assigned by the
   append-only store, not the emitter): EVT_TS, EVT_CD, USR_ID, ENT_NAME, ENT_ID, OLD_VAL,
   NEW_VAL — from the AUD_EVENT definition in legacy_schema.sql.
9. ENT_ID per table PK from legacy_schema.sql: CASE_MASTER→CASE_ID ("C00000042"),
   USR_MASTER→USR_ID (the row's own "U0000009", not the acting user).
10. `ts` and `user` are injected and passed through verbatim (determinism: never read the wall
    clock) — checked with a distinct timestamp and acting user.
11. OPP_MASTER cfg order is STAT_CD, AMT, OWNER_UID (lines 5–7). With STAT_CD and OWNER_UID
    changed and AMT unchanged, events are exactly [(Q→N), (U0000002→U0000003)].
12. Cross-check test re-parses the legacy cfg in-test and, for every listed table, changes all
    its audited columns plus one unaudited column: emitted OLD_VALs must be exactly the cfg
    columns' values in cfg order — this pins the baked-in module config to the artifact.
13. Security/scan expectation: no network/subprocess imports (as in the VAL-01 exemplar).
