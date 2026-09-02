# AUD-03 Target Specification

Migrate legacy AUD_EVENT rows (schema: `legacy/legacy_schema.sql`; sample rows:
`legacy/aud_event_sample.csv`; semantics: `legacy/SEMANTICS_EXCERPT.md` = SYSTEM_OVERVIEW.md §8)
to modern JSON-style events held in an **append-only store**. §8 is binding: "Audit rows are
append-only; migrations must preserve append-only behavior".

## Required interface (one module `migrated.py`)

```python
def migrate_event(row: dict) -> dict: ...

class AuditStore:
    def append(self, event: dict) -> None: ...
    def events(self) -> list[dict]: ...
    def __len__(self) -> int: ...

def migrate(rows: list[dict], store: AuditStore | None = None) -> AuditStore: ...
```

## Required behavior

1. **`migrate_event(row)`** maps one legacy CSV row (string values, AUD_EVENT column names) to:
   - `"evt_id"`: `int(row["EVT_ID"])`
   - `"ts"`: EVT_TS `YYYYMMDDHHMMSS` reformatted to ISO-8601 `YYYY-MM-DDTHH:MM:SS`
     (pure re-slicing of the 14 digits; no timezone, no clock reads)
   - `"code"`: EVT_CD verbatim; `"user_id"`: USR_ID; `"entity"`: ENT_NAME;
     `"entity_id"`: ENT_ID; `"old_val"`/`"new_val"`: OLD_VAL/NEW_VAL verbatim strings
     (empty stays empty). Exactly these eight keys.
2. **`migrate(rows, store=None)`** creates a new `AuditStore` when `store` is None, migrates
   the given rows **in ascending numeric EVT_ID order regardless of input order** (EVT_ID is
   the canonical legacy event order), appends each migrated event, and returns the store.
   **Idempotent re-migration**: an event whose `evt_id` is already present in the store is
   skipped, so migrating the same batch twice (or overlapping batches) never duplicates events.
3. **`AuditStore` is append-only.** `append()` is the *only* mutating operation. The class must
   expose **no** update/delete/replace surface: no attribute named `update`, `delete`,
   `remove`, `pop`, `clear`, `replace`, `__setitem__`, or `__delitem__` may exist on it.
   `events()` returns a defensive copy (list of copied event dicts): mutating the returned
   list or its dicts must not affect the store's contents. `len(store)` is the event count.
4. Append order is preserved: `events()` lists events in the order appended.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
