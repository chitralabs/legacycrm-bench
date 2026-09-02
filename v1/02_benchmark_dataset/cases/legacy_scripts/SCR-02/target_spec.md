# SCR-02 Target Specification

Migrate the nightly CRMScript job `legacy/credit_hold_sweep.crms` (language semantics in
`legacy/SEMANTICS_EXCERPT.md`) to the modern platform as **one Python module**
`migrated.py`.

## Required interface

```python
def sweep(accounts: list[dict], orders: list[dict]) -> tuple[list[dict], list]: ...
```

- `accounts`: ACCT_MASTER rows; `orders`: ORD_HEADER rows (any accounts' orders mixed).
  Numeric fields may be numbers or numeric strings; empty/missing behaves as 0 (NVL).
- Returns `(new_accounts, audits)`: `new_accounts` are **new** dicts in the input order
  (inputs never mutated) with `CRED_HOLD` updated where the sweep changes it; `audits` is
  a list of `(code, acct_id)` tuples.

## Required behavior (from credit_hold_sweep.crms)

1. **Eligibility**: only live (`DEL_FLG <> 'Y'`) customer accounts (`ACCT_TYP == 'C'`) are
   processed; all other accounts are returned unchanged and emit no audits.
2. **Processing order**: `FOR EACH` iterates live rows **ordered by primary key
   ascending**, so accounts are processed (and audits emitted) in ascending `ACCT_ID`
   order regardless of input list order. Returned accounts keep the input list order.
3. **Exposure** per account = sum of `NVL(TOT_AMT,0)` over that account's orders with
   `DEL_FLG <> 'Y'` and `STAT_CD == 'I'` (invoiced only; E/A/S/X and soft-deleted orders
   never count).
4. **Hold on**: if `exposure > NVL(CRED_LIMIT,0)` and `CRED_HOLD != 'Y'` (blank counts as
   not held), set `CRED_HOLD = 'Y'` and emit `("CRED_HOLD_ON", acct_id)`.
5. **Release** (evaluated *after* rule 4, same pass, per the script's second IF): if
   `exposure <= NVL(CRED_LIMIT,0) * 8 / 10` and `CRED_HOLD == 'Y'`, set `CRED_HOLD = 'N'`
   and emit `("CRED_HOLD_OFF", acct_id)`. Note `<=`: exposure exactly 80% of the limit
   releases.
6. **Hysteresis band**: when `80% of limit < exposure <= limit`, neither IF fires — a held
   account stays held and a clear account stays clear, with no audit. Boundary: exposure
   exactly equal to the limit is *not* `>` limit (no hold-on).
7. Exact decimal comparison at the boundaries (80% of the limit must not be distorted by
   binary floating point).
8. No audit is ever emitted for an account whose `CRED_HOLD` did not change.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
