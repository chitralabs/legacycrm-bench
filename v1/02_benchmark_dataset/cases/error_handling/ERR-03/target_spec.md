# ERR-03 Target Specification

Migrate legacy VRL validation-failure reporting (rule file: `legacy/validation_rules.vrl`;
semantics: `legacy/SEMANTICS_EXCERPT.md` = SYSTEM_OVERVIEW.md §2) to a modern RFC-7807-style
problem document as **one Python module** `migrated.py`. Every legacy error code and severity
must survive the migration, in order — and **only** legacy codes may exist in the modern system.

## Required interface

```python
def problem_details(errors: list[dict]) -> dict: ...
```

- `errors`: the collected failures of one write, as produced by the migrated validators
  (VAL-01 style): each entry is `{"code": "<E-code>", "message": str, "severity":
  "BLOCK"|"WARN"}`, already in rule-file collection order.

## Required behavior

1. **Code registry (hallucination guard).** The set of valid legacy error codes is exactly the
   set of `ERROR E....` codes appearing in `validation_rules.vrl` (25 codes: E1001–E1005,
   E2001–E2004, E3001–E3007, E4001–E4004, E5001–E5005). `problem_details` must raise
   `ValueError` if any input entry carries a code outside this registry. No other code may
   ever appear in the output, and the module must not contain any E-code literal absent from
   the rule file.
2. **Blocked flag** per §2 severity semantics: `blocked` is True iff at least one failure has
   severity BLOCK (WARN failures alone allow the write).
3. **Result shape** — exactly these keys:
   - `"type"`: the fixed URI `"https://meridian-crm.example/problems/validation"`;
   - `"title"`: the fixed string `"Legacy validation failed"`;
   - `"status"`: `422` when blocked, else `200` (WARN-only or no failures — the legacy engine
     allows the write);
   - `"blocked"`: bool per rule 2;
   - `"errors"`: a list with **one entry per input entry, in the same order** (no
     de-duplication, no re-sorting, no dropping), each entry exactly
     `{"code", "message", "severity"}` with values preserved verbatim.
4. Empty input (`[]`) is a valid, non-blocked document with `errors == []` and status 200.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
