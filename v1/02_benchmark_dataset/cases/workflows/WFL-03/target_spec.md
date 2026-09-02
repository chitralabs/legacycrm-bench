# WFL-03 Target Specification

Migrate the legacy `order_fulfilment` workflow (`legacy/order_fulfilment.xml`, engine
semantics in `legacy/SEMANTICS_EXCERPT.md`) to the modern platform as **one Python module**
`migrated.py`. This workflow's A→X cancel guard uses VRL `LOOKUP` against ACCT_MASTER, so
the transition function receives in-memory tables.

## Required interface

```python
def fire(state: str, event: str, record: dict, tables: dict) -> dict: ...
```

- `tables`: dict mapping legacy table names to lists of row dicts, e.g.
  `{"ACCT_MASTER": [{"ACCT_ID": "...", "CRED_HOLD": "...", "DEL_FLG": "..."}, ...]}`.
  Missing table keys behave as empty tables.
- Returns a dict with exactly the keys `state`, `record`, `audits`, `notifies`, `matched`
  under the same contract as the legacy engine (§3): `record` is a new dict (input never
  mutated; this workflow has no `<set>` actions, so it is always an unmodified copy);
  `audits` in action order (`["WF_NOMATCH"]` on no-match); `notifies` in action order;
  `matched` True iff a transition fired.

## Required behavior

1. First-match-in-document-order among transitions with matching `from` state, event, and
   TRUE guard. Transition priority matters: the three `cancel` rows are distinguished by
   their `from` state — a cancel from state I must fire the I→X row (ORD_CANC_INV +
   credit_note), never the E→X or A→X rows.
2. `approve` guard `NVL(TOT_AMT,0) > 0`: empty/missing TOT_AMT coerces to 0 → guard FALSE.
3. A→X `cancel` guard `LOOKUP(ACCT_MASTER, ACCT_ID, ACCT_ID, CRED_HOLD) <> 'Y'`:
   LOOKUP scans the ACCT_MASTER table for the **first live row** (DEL_FLG ≠ 'Y') whose
   ACCT_ID equals the record's ACCT_ID and returns its CRED_HOLD value; it returns the
   empty string when no live row matches (missing account, or account soft-deleted).
   Therefore the cancel is blocked only when a *live* account row has CRED_HOLD == 'Y';
   a missing or soft-deleted account yields `'' <> 'Y'` → TRUE → cancel allowed.
4. I→X `cancel` (invoiced order) emits audit `ORD_CANC_INV` and notify `credit_note`.
5. An event with no matching transition (including a guard-blocked cancel from A, and
   cancel from S or X) is a **no-op**: same state, unchanged record copy,
   `audits == ["WF_NOMATCH"]`, `notifies == []`, `matched == False`. Never an error.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
