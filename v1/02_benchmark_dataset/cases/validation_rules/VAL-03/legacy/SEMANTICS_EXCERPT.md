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
- A rule *passes* when its expr evaluates TRUE. On failure: SEVERITY BLOCK (default) rejects the
  write with the error code; SEVERITY WARN allows the write and logs a `VAL_WARN` audit event.
- Rules run in file order; **all** BLOCK failures for the write are collected and reported together
  (the legacy engine does not stop at the first failure).

## 3. Workflow engine — semantics
