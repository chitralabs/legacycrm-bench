# Excerpts from SYSTEM_OVERVIEW.md (Meridian CRM 4.2, authoritative semantics)

## 1. Entities and storage (conventions, excerpt)

- Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`.
- Amounts stored as `NUMBER`; empty string in numeric context coerces to 0.

## 2. VRL — semantics (excerpt)

- `OLD.<col>` is the pre-update value. A rule *passes* when its expr evaluates TRUE;
  on failure, SEVERITY BLOCK (default) rejects the write with the error code.
- Empty string in numeric comparison coerces to 0. `NVL(x, default)` returns `default`
  when `x` is empty/missing.

Rule in scope (`account_rules.vrl`): ACC-004 — an UPDATE that releases a credit hold
(OLD.CRED_HOLD='Y' → CRED_HOLD='N') while CRED_LIMIT <= 0 is rejected with
`E1004 "Cannot release credit hold with zero credit limit"`.

## 4. CRMScript — audit codes (excerpt from credit_hold_sweep.crms)

The nightly sweep releases holds with `UPDATE acct SET CRED_HOLD = 'N'` followed by
`CALL AUDIT('CRED_HOLD_OFF', acct.ACCT_ID)` — `CRED_HOLD_OFF` is the documented audit
code for a successful release, keyed by account id.
