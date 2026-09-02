# WFL-01 Target Specification

Migrate the legacy `opportunity_pipeline` workflow (`legacy/opportunity_pipeline.xml`,
engine semantics in `legacy/SEMANTICS_EXCERPT.md`) to the modern platform as **one Python
module** `migrated.py`.

## Required interface

```python
def fire(state: str, event: str, record: dict) -> dict: ...
```

Returns a dict with exactly these keys:

- `"state"`: the resulting state code (unchanged on no-match).
- `"record"`: a **new** dict (the input `record` must not be mutated) with all `<set>`
  actions applied; on no-match, an unmodified copy of the input.
- `"audits"`: list of audit codes emitted, in action order; `["WF_NOMATCH"]` on no-match.
- `"notifies"`: list of notify template names emitted, in action order; `[]` on no-match.
- `"matched"`: `True` iff a transition fired.

## Required behavior (legacy engine semantics, §3)

1. A transition fires iff `state == from`, the event name matches, and its guard (if any)
   evaluates TRUE against `record`. If several transitions could match, the **first in
   document order** of the XML wins.
2. An event with no matching transition is a **no-op**: same state, unchanged record copy,
   `audits == ["WF_NOMATCH"]`, `notifies == []`, `matched == False`. It is not an error.
3. `<set>` actions apply after the state change, in document order. Literal `value`
   attributes are applied exactly as the literal string from the XML (e.g. `STAGE_PCT`
   becomes the string `"25"`).
4. Guard expression semantics (VRL): `NVL(x, d)` returns `d` when `x` is empty/missing;
   empty string coerces to 0 in numeric comparison (so `NVL(AMT,0) > 0` is FALSE for
   `AMT` of `""`, `"0"`, or `0`). `CLOSE_DT <> '00000000'` is plain string inequality
   against the sentinel literal (equality/inequality to `'00000000'` is the only defined
   comparison against the sentinel). `LOST_RSN <> ''` is TRUE iff the field is a non-empty
   string; missing fields read as empty string.
5. Audit codes and notify templates are collected in action order into `audits`/`notifies`.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
