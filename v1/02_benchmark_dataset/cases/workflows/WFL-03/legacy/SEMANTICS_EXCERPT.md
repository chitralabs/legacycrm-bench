# Excerpts from legacy_system/SYSTEM_OVERVIEW.md (Meridian CRM 4.2)

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

## 2. Validation Rule Language (VRL) — expression semantics (used by guards)

- `<expr>` grammar: comparisons (`=`, `<>`, `<`, `<=`, `>`, `>=`), arithmetic (`+ - * /`),
  `AND`, `OR`, `NOT`, parentheses; functions `LEN(x)`, `UPPER(x)`, `SUBSTR(x,start,len)` (1-based),
  `NVL(x, default)`, `TODAY()`, `LOOKUP(TABLE, key_col, key_val, out_col)` (returns matching
  column value or empty string if no live row). Field references are bare column names.
- Empty string in numeric comparison coerces to 0. Date comparisons are lexicographic on the
  `YYYYMMDD` string, with sentinel `00000000` treated as "no value": any comparison against it is
  FALSE except explicit equality to `'00000000'`.

## 1. Legacy conventions (relevant subset)

- Dates stored as `VARCHAR2(8)` in `YYYYMMDD`; the sentinel `00000000` means NULL.
- Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`.
- Soft delete: `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them unless stated.
