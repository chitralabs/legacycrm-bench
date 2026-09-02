# RIN-02 Target Specification

Migrate the legacy ORD_LINE renumbering invariant (`legacy/ord_line_schema.sql`,
conventions `legacy/SEMANTICS_EXCERPT.md`: "LINE_NO starts at 1, increments by 1, and
gaps are forbidden after renumbering") as **one Python module** `migrated.py`.

## Required interface

```python
def renumber(lines: list[dict]) -> list[dict]: ...
```

`lines` are ORD_LINE rows (dicts; LINE_NO may be an int or a numeric string; missing
keys behave as empty string). Rows may belong to more than one ORD_ID.

## Required behavior

1. Soft-deleted lines (`DEL_FLG='Y'`; blank means `N`) are **removed** — they do not
   appear in the output and do not occupy a line number.
2. Renumbering is **per order**: within each ORD_ID, the surviving lines keep their
   relative order (by original LINE_NO, compared **numerically** — "2" before "10")
   and are assigned `LINE_NO` = 1, 2, 3, ... as **ints**.
3. The returned list is ordered by (ORD_ID ascending as a string, new LINE_NO
   ascending). All other fields of each row are preserved unchanged.
4. **Idempotent:** `renumber(renumber(x)) == renumber(x)` for any input.
5. **Pure:** the input list and its row dicts are not mutated; returned rows are new
   dicts.
6. Empty input (or input whose rows are all soft-deleted) returns `[]`.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
