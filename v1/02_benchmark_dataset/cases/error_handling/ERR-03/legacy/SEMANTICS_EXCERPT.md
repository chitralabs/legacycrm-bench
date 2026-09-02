# Excerpt of legacy_system/SYSTEM_OVERVIEW.md (authoritative semantics)

## 2. Validation Rule Language (VRL) — semantics (relevant part)

Each rule: `RULE <rule_id> ON <TABLE> WHEN <event-list> : <expr> ELSE ERROR <code> "<message>"
[SEVERITY <BLOCK|WARN>]`.

- A rule *passes* when its expr evaluates TRUE. On failure: SEVERITY BLOCK (default) rejects the
  write with the error code; SEVERITY WARN allows the write and logs a `VAL_WARN` audit event.
- Rules run in file order; **all** BLOCK failures for the write are collected and reported together
  (the legacy engine does not stop at the first failure).

The complete set of legacy error codes is exactly the set of `ERROR E....` codes appearing in
`validation_rules.vrl`; no other error codes exist in the legacy system.
