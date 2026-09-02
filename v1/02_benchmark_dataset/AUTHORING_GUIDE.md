# LegacyCRM-Bench Case Authoring Guide (internal, v0.1)

This guide directs authoring of the 36-case pilot benchmark. Read, in order:
1. `CASE_FORMAT.md` (binding contract; the validator enforces it)
2. `legacy_system/SYSTEM_OVERVIEW.md` (authoritative semantics — the ONLY source of expected behavior)
3. The exemplar case `cases/validation_rules/VAL-01/` (structure, tone, test style)

## Binding rules

- Expected test values must be derivable by hand from the documented semantics; write the
  derivation in `GROUND_TRUTH.md` (numbered, one entry per non-obvious expectation). Never
  copy expectations from an unexplained computation.
- Tests: pytest + stdlib only; deterministic; inject `today` where needed; use `case_lib`
  helpers; deliverables imported inside fixtures/tests (never at module top level); 8–20
  tests; ≥1 negative expectation; a security-scan test where `security_expectations` is
  non-trivial. Prefer small hand-crafted fixture rows inline in tests over the 700-row seed
  data (seed data may be used only when GROUND_TRUTH.md documents the exact calculation).
- Reference solutions: stdlib only (sqlite3 allowed), deterministic, no network/subprocess,
  only the files listed in `deliverables`.
- Every case must pass: `validate_cases.py` (0 errors), `run_case.py --solution reference`
  (100% pass), `run_case.py --solution null` (0 tests passed).
- Each case's `legacy/` contains copies/excerpts of the relevant `legacy_system/` artifacts
  plus a `SEMANTICS_EXCERPT.md` of the relevant SYSTEM_OVERVIEW sections (like VAL-01).
- Do not duplicate another case's oracle: each case tests a distinct behavior slice.

## Commands (run from v1/)

```
.venv/bin/python 03_source_code/harness/validate_cases.py
.venv/bin/python 03_source_code/harness/run_case.py --case 02_benchmark_dataset/cases/<cat>/<ID> --solution reference
.venv/bin/python 03_source_code/harness/run_case.py --case 02_benchmark_dataset/cases/<cat>/<ID> --solution null
```

## Case designs (36 = 12 categories × 3; VAL-01 already authored)

### schema_mapping (SCH)
- **SCH-01 easy** — ACCT_MASTER → modern `account` mapping: deliver `migrated.py` with
  `convert_account(row: dict) -> dict | None` (None for soft-deleted): sentinel dates → None or
  ISO `YYYY-MM-DD`, `CHAR(1)` Y/N → bool, blank CURR_CD → "USD", NUMBER strings → float/int,
  key rename to snake_case per a mapping table given in target_spec.
- **SCH-02 medium** — CONT_MASTER mapping incl. PREF_CH enum (blank→"email"), OPTOUT_FLG →
  `marketing_optout: bool`, empty EMAIL_TX → None, and a `convert_all(rows)` that drops
  soft-deleted rows and preserves input order.
- **SCH-03 hard** — OPP_MASTER: collapse redundant STAT_CD/STAGE_PCT into one `stage` enum
  (trust STAT_CD; when STAGE_PCT disagrees, still map from STAT_CD but add
  `"migration_flags": ["stage_pct_mismatch"]`), convert AMT to integer minor units with
  currency-aware exponent (JPY has 0 decimals — say so in target_spec), sentinel CLOSE_DT.

### validation_rules (VAL; VAL-01 done)
- **VAL-02 easy** — ACC-001..ACC-005 (`legacy/account_rules.vrl`): includes OLD.-based
  credit-hold release rule (UPDATE only) and ACC-005 WARN. Same interface as VAL-01.
- **VAL-03 hard** — ORD-001..ORD-005 with `LOOKUP`: interface
  `validate(record, old, event, tables)` where `tables` is a dict of in-memory tables
  (e.g. {"USR_MASTER": [...], "PROD_MASTER": [...]}); LOOKUP ignores soft-deleted rows and
  returns "" on miss (so ORD-005 fails when product is missing OR inactive OR soft-deleted;
  ORD-002 must treat unknown user's role as "" → rule fails when DISC_PCT > 20).

### workflows (WFL)
- **WFL-01 easy** — opportunity_pipeline: `migrated.py` with
  `fire(state, event, record) -> dict` returning `{"state", "record", "audits", "notifies",
  "matched": bool}`; guards, first-match-in-document-order, no-match → same state +
  `audits=["WF_NOMATCH"]` + matched False.
- **WFL-02 medium** — case_lifecycle minus timers: `<set>` actions apply after state change in
  order (reopen R→A clears RES_DT to "00000000"), audit codes collected in action order.
- **WFL-03 hard** — order_fulfilment with LOOKUP guard (A→X cancel blocked when account
  CRED_HOLD='Y' — `fire(state, event, record, tables)`), I→X emits ORD_CANC_INV + credit_note
  notify; verify transition priority when multiple `cancel` rows could match.

### legacy_scripts (SCR)
- **SCR-01 easy** — order_totals.crms → `recompute(order, lines) -> (order, lines, audits)`;
  EXT_AMT = QTY*UNIT_PRC; TOT_AMT = total*(100-DISC_PCT)/100 rounded half-up to cents;
  ORD_RETOTAL audit only when TOT_AMT changed; skip STAT_CD='X' and soft-deleted lines.
- **SCR-02 medium** — credit_hold_sweep.crms → `sweep(accounts, orders) -> (accounts, audits)`;
  exposure = Σ TOT_AMT of live invoiced orders; hold when exposure > limit; release only when
  exposure ≤ 80% of limit (hysteresis band: no change between 80% and 100%); only ACCT_TYP='C'
  live accounts; audit codes CRED_HOLD_ON/OFF with account ids.
- **SCR-03 hard** — case_escalation.crms → `escalate(cases, today) -> list[event]` producing
  workflow events per DATEDIFF day-granularity rules (N≥2 days; A≥7 days AND ESC_FLG≠'Y');
  DATEDIFF sentinel rule (either date 00000000 → 0 days → never overdue); verify boundary
  days exactly (1 day: no, 2 days: yes).

### rbac (RBC)
- **RBC-01 easy** — `can(user, action, object, record, role_rows) -> bool`: deny-by-default,
  OWN/TEAM/ALL scopes vs OWNER_UID/TEAM_CD; NONE scope denies.
- **RBC-02 medium** — ADMIN semantics (row must exist; scope ignored → ALL) + DELETE requires
  record DEL_FLG='N'; negative tests: ADMIN without a row for (object,action) is denied
  (no silent privilege widening).
- **RBC-03 hard** — deliver `policy.json` (modern policy doc; schema in target_spec) +
  `migrated.py` with `can()` reading it; equivalence test enumerates the full cross-product of
  hand-crafted users × records × actions × objects (≥200 tuples generated in-test from the
  legacy matrix excerpt) asserting decision-for-decision equality with legacy semantics —
  any widening is a failure; include a source-scan test that policy.json contains no role
  granting objects/actions absent from the legacy matrix.

### integration (INT)
- **INT-01 easy** — endpoints.ini → `endpoints.json` (schema in target_spec): auth split into
  `{"type": "basic"|"apikey"|"none", "secret_ref": "vault://..."|null}`; security test: no
  literal credential patterns anywhere in deliverables; retry/timeout as integers.
- **INT-02 medium** — EXPORT_ACCT fixed-width formatter from the LAYOUT rows of
  data_dictionary.csv: `format_account(row) -> str` (exact 77-char record: verify each field
  slice; ANN_REV cents zero-padded 15 wide; blank CRED_HOLD written as 'N'; name truncated
  at 40).
- **INT-03 hard** — marketing_sync CSV payload builder: `build_payload(contacts) -> str`;
  excludes OPTOUT_FLG='Y' and soft-deleted contacts (privacy preservation — negative tests
  that an opted-out contact NEVER appears), PREF_CH blank → 'E', RFC-4180-style quoting for
  values containing commas/quotes, header row fixed.

### batch_processing (BAT)
- **BAT-01 easy** — batch_jobs.cfg → `schedule.json`: parse JOB lines to
  `{"name", "at", "script", "on_error": {"policy", "retries"}}` preserving file order;
  default ON_ERROR policy is ABORT when the clause is absent (per §7 sequential semantics —
  state this in target_spec).
- **BAT-02 medium** — runner semantics: `run_jobs(jobs, executor) -> log` where executor is an
  injected callable that may raise; ABORT stops the whole schedule, CONTINUE logs
  BATCH_ROWSKIP and proceeds to next job, RETRY:n re-invokes up to n additional times then
  aborts if still failing; log records attempts per job in order.
- **BAT-03 hard** — chunked export: `export_chunks(rows, send) -> int` (dw_export batching):
  chunks of exactly 500 via injected `send(payload)`, final partial chunk sent iff non-empty,
  rows joined with "\n" and trailing newline per record, returns records sent; test with 0,
  1, 499, 500, 501, 1000 synthetic rows (construct in-test).

### error_handling (ERR)
- **ERR-01 easy** — legacy div-by-zero quirk: `safe_div(a, b) -> (value, audits)` and
  expression contexts preserving div0 → 0 + SCRIPT_DIV0 audit; negative test: no exception
  propagates.
- **ERR-02 medium** — endpoint retry wrapper: `call_with_retry(endpoint_cfg, transport)` with
  injected transport raising TransientError/PermanentError; attempts = retry+1 on transient,
  exactly 1 on permanent, returns last error info; timeout_ms passed through.
- **ERR-03 hard** — error-code preservation: modern `problem_details(errors) -> dict` mapping
  collected VRL failures to an RFC-7807-shaped dict retaining every legacy code/severity in
  order, blocked flag consistent with is_blocked semantics; negative tests for dropped or
  re-ordered codes and invented codes (hallucination check: only E-codes from the legacy rule
  file may appear).

### audit_logging (AUD)
- **AUD-01 easy** — audit_config.cfg parser: `audited_columns() -> dict[table, set]`;
  membership tests + negative (unlisted column not audited).
- **AUD-02 medium** — `emit_audits(table, old, new, user, ts) -> list[event]`: one event per
  changed audited column, OLD_VAL/NEW_VAL stringified, unchanged/unaudited columns emit
  nothing; event field names per AUD_EVENT schema; order follows audit_config file order for
  that table (state this in target_spec).
- **AUD-03 hard** — migrate legacy AUD_EVENT rows to modern JSON events: EVT_TS
  YYYYMMDDHHMMSS → ISO-8601 `YYYY-MM-DDTHH:MM:SS`, preserve EVT_ID order, append-only store
  class `AuditStore` whose `append()` is the only mutator (negative tests: no update/delete
  API mutates existing events; re-migration is idempotent).

### referential_integrity (RIN)
- **RIN-01 easy** — orphan detection matching integrity_check.crms LOOKUP semantics:
  `find_orphans(contacts, accounts) -> list[ids]`; a contact pointing at a soft-deleted
  account IS an orphan (LOOKUP sees live rows only); soft-deleted contacts skipped.
- **RIN-02 medium** — ORD_LINE renumber: `renumber(lines) -> lines` making LINE_NO contiguous
  from 1 preserving relative order after soft-deleted lines are removed; idempotent.
- **RIN-03 hard** — deliver `modern_schema.sql` (SQLite DDL) with real FK constraints +
  `migrated.py` `load(conn, tables)`; tests run sqlite3 with `PRAGMA foreign_keys=ON`,
  assert orphan inserts now fail, ON DELETE behavior per target_spec (orders RESTRICT,
  ORD_LINE CASCADE from header — mirroring documented app behavior), and that loading
  cleaned seed-like fixture data succeeds.

### business_rules (BIZ)
- **BIZ-01 easy** — credit-hold release guard (ACC-004) as modern service:
  `release_credit_hold(account) -> account | raise BusinessRuleViolation(code)`; only
  Y→N with CRED_LIMIT>0 allowed; audit event on success.
- **BIZ-02 medium** — discount policy (ORD-002): `set_discount(order, pct, user, users) ->`
  result; >20% requires MGR or ADMIN role (soft-deleted/unknown users have no role);
  boundary tests at exactly 20 and 20.01.
- **BIZ-03 hard** — invoiced-order rules: combine E5003 (invoiced order may only move to X)
  with order_fulfilment I→X actions (ORD_CANC_INV audit + credit_note notify) and header
  recompute after line change is forbidden for STAT_CD='I' (state in target_spec: invoiced
  totals frozen); cross-checks that a migration preserving only the workflow OR only the
  validation rule fails.

### config_modernization (CFG)
- **CFG-01 easy** — code tables → `enums.json`: STAT_CD/SEV_CD/ACT_TYP/etc. code→label maps
  extracted from data_dictionary.csv COLUMN rows; exact label fidelity (e.g., "Closed-Won"),
  no invented codes (hallucination negative test).
- **CFG-02 medium** — legacy conventions utility module: `to_iso(yyyymmdd) -> str|None`
  (sentinel → None), `from_iso`, `yn(char) -> bool` (blank → False), `to_minor_units(amount,
  currency)` (blank currency → USD, JPY exponent 0), round-trip properties tested.
- **CFG-03 hard** — workflows.xml → `workflows.json` structural migration (schema in
  target_spec): every workflow/state/transition/guard/action preserved with counts equal to
  the XML, document order retained, guards kept as strings verbatim; hallucination negative
  test (no transition in JSON absent from XML) and completeness test (none missing);
  initial-state flags preserved.

## Difficulty & metadata

Difficulties fixed as listed above. num_tests: honest count. security_expectations: non-trivial
for INT-01, INT-03, RBC-*, AUD-03, RIN-03, CFG-03 (hallucination), ERR-03 (hallucination).
