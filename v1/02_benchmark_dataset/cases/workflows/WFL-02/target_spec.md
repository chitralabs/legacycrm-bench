# WFL-02 Target Specification

Migrate the legacy `case_lifecycle` workflow (`legacy/case_lifecycle.xml`, engine semantics
in `legacy/SEMANTICS_EXCERPT.md`) to the modern platform as **one Python module**
`migrated.py`. **Timers are out of scope**: only explicit event dispatch is migrated (the
`<timer>` elements describe when the nightly batch *posts* `auto_escalate`; posting is not
part of this module — handling a posted `auto_escalate` event is).

## Required interface

```python
def fire(state: str, event: str, record: dict) -> dict: ...
```

Returns a dict with exactly these keys (same contract as the legacy engine, §3):

- `"state"`: resulting state code (unchanged on no-match; note A→A self-transition keeps
  the state "A" with `matched == True`).
- `"record"`: a **new** dict (input never mutated) with `<set>` actions applied; an
  unmodified copy on no-match.
- `"audits"`: audit codes in action order; `["WF_NOMATCH"]` on no-match.
- `"notifies"`: notify template names in action order; `[]` on no-match.
- `"matched"`: `True` iff a transition fired.

## Required behavior

1. First-match-in-document-order among transitions whose `from` == state, event matches,
   and guard (if any) is TRUE.
2. `<set>` actions apply **after** the state change, in document order, to the evolving
   record copy. Literal values are applied as the literal string from the XML
   (`ESC_FLG` → `"Y"`, `RES_DT` → `"00000000"`).
3. A value starting with `=` is a VRL expression evaluated against the evolving record:
   `=NVL(SEV_CD,'3')` yields the record's `SEV_CD` when it is non-empty, else the string
   `"3"` (NVL returns the default for empty/missing values).
4. Guards use VRL semantics: `OWNER_UID <> ''` is TRUE iff non-empty (missing keys read as
   empty string); `ESC_FLG <> 'Y'` is TRUE for `"N"`, `""`, or missing; `RES_DT <>
   '00000000'` is string inequality against the sentinel literal.
5. No-match (e.g. `resolve` while `RES_DT` is the sentinel, or any event from state X) is a
   no-op that logs `WF_NOMATCH` — never an exception.
6. A transition with no `<actions>` (P→A `customer_reply`) fires with empty `audits` and
   `notifies`.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
