# Meridian CRM 4.2 — Synthetic Legacy System Specification

**Provenance:** Meridian CRM is a *fictional* legacy CRM product invented for LegacyCRM-Bench.
All artifacts here were authored by the benchmark project (2026-09-01) and contain no material
from any real vendor, employer, customer, or proprietary system. Any resemblance to real products
is limited to generic industry conventions (entities such as accounts, contacts, opportunities).
License: CC BY 4.0 (data/specs), MIT (code). This document is the **authoritative semantics
specification**: all acceptance-test expected values are derived from the rules written here and
in the artifact files, never from an LLM.

Meridian CRM 4.2 represents a common pattern: an early-2000s on-premises CRM with a relational
store, application-enforced integrity (no declarative foreign keys), a proprietary validation-rule
DSL (VRL), XML workflow definitions, a BASIC-like scripting language (CRMScript), INI-style
integration and batch configuration, and a fixed-format audit log.

## 1. Entities and storage

Schema: `legacy_schema.sql` (legacy SQL dialect: `VARCHAR2`, `NUMBER`, no FK constraints — referential
integrity is enforced by application code and nightly batch checks). Column semantics: `data_dictionary.csv`.

Entities: ACCT_MASTER (accounts), CONT_MASTER (contacts), OPP_MASTER (opportunities), CASE_MASTER
(support cases), PROD_MASTER (products), ORD_HEADER/ORD_LINE (orders), ACT_LOG (activities),
USR_MASTER (users), ROLE_DEF (roles; the permission matrix lives in the exported
`role_permissions.csv` artifact rather than a schema table), INT_ENDPOINT (integration endpoints),
AUD_EVENT (audit events).

Legacy conventions that migrations must handle:
- **Sentinel values.** Dates stored as `VARCHAR2(8)` in `YYYYMMDD`; the sentinel `00000000` means NULL.
  Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`. Amounts stored as `NUMBER(15,2)` in the
  account's currency; currency code in `CURR_CD` (ISO-4217), blank means `USD`.
- **Status codes.** Single-letter codes with meanings fixed in `data_dictionary.csv`
  (e.g., OPP_MASTER.STAT_CD: P=Prospecting, Q=Qualified, N=Negotiation, W=Closed-Won, L=Closed-Lost).
- **Soft delete.** `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them unless stated.
- **No currency conversion.** The legacy engine compares and aggregates monetary amounts
  raw, ignoring CURR_CD (a known legacy defect migrations must preserve unless a case's
  target spec says otherwise).
- **Monetary rounding.** All stored monetary amounts are rounded half-up to cents at write
  time (the convention every batch recompute follows).
- **Composite keys.** ORD_LINE key is (ORD_ID, LINE_NO); LINE_NO starts at 1, increments by 1, and gaps
  are forbidden after renumbering.

## 2. Validation Rule Language (VRL) — semantics

File: `validation_rules.vrl`. Line-oriented; `#` starts a comment. Each rule:

```
RULE <rule_id> ON <TABLE> WHEN <event-list> : <expr> ELSE ERROR <code> "<message>" [SEVERITY <BLOCK|WARN>]
```

- `<event-list>`: comma-separated subset of {INSERT, UPDATE}.
- `<expr>` grammar: comparisons (`=`, `<>`, `<`, `<=`, `>`, `>=`), arithmetic (`+ - * /`),
  `AND`, `OR`, `NOT`, parentheses; functions `LEN(x)`, `UPPER(x)`, `SUBSTR(x,start,len)` (1-based),
  `NVL(x, default)`, `TODAY()` (returns current date as `YYYYMMDD` string), `LOOKUP(TABLE, key_col,
  key_val, out_col)` (returns matching column value or empty string if no live row).
  Field references are bare column names of the rule's table; `OLD.<col>` is the pre-update value
  (INSERT: `OLD.<col>` is the empty string / 0 for numeric context).
- Empty string in numeric comparison coerces to 0. Date comparisons are lexicographic on the
  `YYYYMMDD` string, with sentinel `00000000` treated as "no value": any comparison against it is
  FALSE except explicit equality to `'00000000'`.
- VRL has no current-user context: rules reference stored fields only, so approval-style
  rules (e.g., discount limits) key off the *record owner's* role rather than the acting
  user's — a documented legacy quirk.
- A rule *passes* when its expr evaluates TRUE. On failure: SEVERITY BLOCK (default) rejects the
  write with the error code; SEVERITY WARN allows the write and logs a `VAL_WARN` audit event.
- Rules run in file order; **all** BLOCK failures for the write are collected and reported together
  (the legacy engine does not stop at the first failure).

## 3. Workflow engine — semantics

File: `workflows.xml`. Each `<workflow>` has `entity`, a `<states>` list (one `initial="true"`),
`<transition>` elements with `from`, `to`, `event`, optional `<guard>` (VRL expression over the
entity's fields), and optional `<actions>` (list of `<set field="F" value="V"/>`,
`<audit code="..."/>`, `<notify template="..."/>` — notify is queued via INT_ENDPOINT `notifier`).
Semantics:
- A transition fires iff current state = `from`, event name matches, and guard (if any) is TRUE.
- If several transitions match, the **first in document order** wins.
- `<set>` actions apply after the state change, in order. `value` may be a literal or `=EXPR` (VRL expr).
- An event with no matching transition is a **no-op that logs** audit code `WF_NOMATCH` (it is not an error).
- Escalation timers: `<timer after_days="N" event="E"/>` inside a state fires event E when the entity
  has been in that state ≥ N days (evaluated by the nightly batch, day granularity).

## 4. CRMScript — semantics

Directory: `scripts/`. BASIC-like, line-oriented; case-insensitive keywords; `'` starts comment.
Statements: `LET var = expr`, `IF expr THEN ... [ELSE ...] END IF`, `FOR EACH row IN <TABLE> [WHERE expr] ... NEXT`
(iterates live rows, ordered by primary key ascending), `UPDATE row SET col = expr`,
`INSERT INTO <TABLE> (cols...) VALUES (exprs...)`, `CALL AUDIT(code, entity_id)`,
`CALL HTTPPOST(endpoint_name, payload_expr)`, `RETURN expr`, `EXIT FOR`.
Expressions use VRL operators/functions plus string concatenation `&` and the additional builtins
`FIXED(s, w)` (left-align, space-pad, truncate to width w), `ZPAD(num, w)` (round half-up to integer,
right-align, zero-pad to width w), `CHR(n)` (character from code point), and `DATEDIFF(d1, d2)`
(whole days d1 − d2 for `YYYYMMDD` strings; 0 if either is the `00000000` sentinel). Numeric division by zero
yields 0 and logs audit `SCRIPT_DIV0` (legacy quirk that migrations must preserve or explicitly
modernize per the case's target spec). Variables are dynamically typed; uninitialized variables
read as empty string.

## 5. RBAC — semantics

`role_permissions.csv` columns: `role_id,object,action,scope`.
Objects are entity names; actions in {READ, CREATE, UPDATE, DELETE, EXPORT}; scope in
{ALL, TEAM, OWN, NONE}. USR_MASTER.ROLE_ID assigns exactly one role. TEAM scope: user's
TEAM_CD must equal the record owner's TEAM_CD (owner = OWNER_UID column). OWN scope: OWNER_UID
must equal the user id. Entities whose physical table lacks a TEAM_CD column (e.g., ORD_HEADER) have the record's
team supplied by the application layer from the owner's USR_MASTER row (OWNER_UID -> TEAM_CD)
before the check runs, so scope checks always see a team attribute on the record image.
Permission checks deny by default: a missing (role, object, action) row
means NONE. Row-level rule: DELETE additionally requires the record to be soft-deletable
(DEL_FLG currently 'N'). The ADMIN role bypasses scope but not object/action rows (an ADMIN row
must still exist for the object/action; its scope is ignored and treated as ALL).

## 6. Integrations — semantics

`endpoints.ini`: INI sections per endpoint with `url`, `auth` (`none` | `basic:<secret_ref>` |
`apikey:<secret_ref>`), `retry` (count), `timeout_ms`, `payload` (`fixed_width` | `csv` | `xml`).
Secrets are **references** into a vault (`vault://...`), never literal credentials. Fixed-width
payload layouts are in `data_dictionary.csv` rows with DICT_TYPE=LAYOUT.

## 7. Batch jobs — semantics

`batch_jobs.cfg`: line format `JOB <name> AT <HH:MM> RUN <script.crms> [ON_ERROR <ABORT|CONTINUE|RETRY:n>]`.
Jobs run sequentially in file order at their scheduled time; RETRY:n re-runs the whole script up to n
times; CONTINUE skips the failing row and logs `BATCH_ROWSKIP`.

## 8. Audit log — semantics

AUD_EVENT columns: EVT_ID, EVT_TS (YYYYMMDDHH24MISS string), EVT_CD, USR_ID, ENT_NAME, ENT_ID,
OLD_VAL, NEW_VAL. Every UPDATE to an audited column (audit_config.cfg lists them) writes one row
per changed column, with OLD_VAL/NEW_VAL as strings. Audit rows are append-only; migrations must
preserve append-only behavior and per-column granularity unless the case's target spec says otherwise.

## 9. Seed data

`seed_data/*.csv` is generated deterministically by `03_source_code/generate_seed_data.py`
(fixed seed 20260901, stdlib `random` only, fictional names from bundled word lists). No real
personal data is used or imitated beyond generic name patterns.
