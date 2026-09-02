# Excerpts from legacy_system/SYSTEM_OVERVIEW.md (Meridian CRM 4.2)

## 4. CRMScript — semantics

Directory: `scripts/`. BASIC-like, line-oriented; case-insensitive keywords; `'` starts comment.
Statements: `LET var = expr`, `IF expr THEN ... [ELSE ...] END IF`, `FOR EACH row IN <TABLE> [WHERE expr] ... NEXT`
(iterates live rows, ordered by primary key ascending), `UPDATE row SET col = expr`,
`INSERT INTO <TABLE> (cols...) VALUES (exprs...)`, `CALL AUDIT(code, entity_id)`,
`CALL HTTPPOST(endpoint_name, payload_expr)`, `RETURN expr`, `EXIT FOR`.
Expressions use VRL operators/functions plus string concatenation `&` and the additional builtins
`FIXED(s, w)`, `ZPAD(num, w)`, `CHR(n)`, and `DATEDIFF(d1, d2)`
(**whole days d1 − d2 for `YYYYMMDD` strings; 0 if either is the `00000000` sentinel**).
Variables are dynamically typed; uninitialized variables read as empty string.
`TODAY()` returns the current date as a `YYYYMMDD` string.

## 3. Workflow engine — timer semantics (context for this job)

- Escalation timers: `<timer after_days="N" event="E"/>` inside a state fires event E when
  the entity has been in that state ≥ N days (evaluated by the nightly batch, day
  granularity). The case_lifecycle workflow has `<timer after_days="2"
  event="auto_escalate"/>` on state N and `<timer after_days="7" event="auto_escalate"/>`
  on state A; this nightly script is the batch that posts those events via
  `CALL WORKFLOW_EVENT('case_lifecycle', case_id, 'auto_escalate')`.

## 1. Legacy conventions (relevant subset)

- Dates stored as `VARCHAR2(8)` in `YYYYMMDD`; the sentinel `00000000` means NULL.
- Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`.
- Soft delete: `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them unless stated.
- CASE_MASTER.STAT_CD: N=New; A=Assigned; P=Pending-Customer; R=Resolved; X=Closed.
