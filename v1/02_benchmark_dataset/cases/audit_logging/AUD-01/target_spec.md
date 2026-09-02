# AUD-01 Target Specification

Migrate the Meridian CRM audited-column configuration parser (artifact:
`legacy/audit_config.cfg`; semantics: `legacy/SEMANTICS_EXCERPT.md` = SYSTEM_OVERVIEW.md §8)
to the modern platform as **one Python module** `migrated.py`.

## Required interface

```python
def audited_columns(cfg_text: str) -> dict[str, set[str]]: ...
```

- `cfg_text` is the full text of an `audit_config.cfg`-format file, **injected as a string**
  (the module performs no file I/O; the caller reads the file). This keeps the parser
  deterministic and testable against both the real legacy artifact and hand-crafted inputs.
- Returns a dict mapping each table name that has at least one `AUDIT` line to the **set** of
  its audited column names. Tables with no `AUDIT` line must be absent from the dict (not
  mapped to an empty set).

## Required parsing behavior (config format, per the artifact and §8)

1. The file is line-oriented. A line whose first non-blank character is `#` is a comment; blank
   (or whitespace-only) lines are ignored.
2. A configuration line has exactly the form `AUDIT <TABLE> <COLUMN>` (single spaces or any
   run of whitespace between tokens). It declares `<COLUMN>` of `<TABLE>` audited.
3. Duplicate declarations of the same (table, column) are idempotent (sets deduplicate).
4. Table and column names are case-sensitive and returned verbatim.
5. Only columns explicitly listed are audited: the parser must not add, infer, or normalize
   any column (§8: "Every UPDATE to an audited column (audit_config.cfg lists them) ...").

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
