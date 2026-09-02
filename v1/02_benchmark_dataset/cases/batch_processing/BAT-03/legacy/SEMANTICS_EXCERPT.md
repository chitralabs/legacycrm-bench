# Excerpts from legacy_system/SYSTEM_OVERVIEW.md (Meridian CRM 4.2)

## 4. CRMScript — semantics (relevant subset)

Directory: `scripts/`. BASIC-like, line-oriented; case-insensitive keywords; `'` starts
comment. Statements include `LET var = expr`,
`IF expr THEN ... [ELSE ...] END IF`, `FOR EACH row IN <TABLE> [WHERE expr] ... NEXT`
(iterates live rows, ordered by primary key ascending), and
`CALL HTTPPOST(endpoint_name, payload_expr)`.
Expressions use VRL operators/functions plus string concatenation `&` and the additional
builtins `FIXED(s, w)` (left-align, space-pad, truncate to width w), `ZPAD(num, w)`
(round half-up to integer, right-align, zero-pad to width w), `CHR(n)` (character from
code point). `CHR(10)` is the newline character.

## 7. Batch jobs — semantics

`batch_jobs.cfg`: line format
`JOB <name> AT <HH:MM> RUN <script.crms> [ON_ERROR <ABORT|CONTINUE|RETRY:n>]`.
Jobs run sequentially in file order at their scheduled time; RETRY:n re-runs the whole
script up to n times; CONTINUE skips the failing row and logs `BATCH_ROWSKIP`.
(dw_export runs nightly at 03:00 with `ON_ERROR RETRY:1`.)
