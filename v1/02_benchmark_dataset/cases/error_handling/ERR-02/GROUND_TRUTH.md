# ERR-02 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/endpoints.ini` and the semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §6, with the §7 retry-count convention: RETRY:n = initial attempt plus
up to n re-attempts). No LLM output was used to produce expectations. Derivations:

1. The module must export `TransientError`/`PermanentError` as Exception subclasses — the
   injected transport signals failure kind by raising them (target-spec interface).
2. Success on the first attempt: exactly one transport call, `ok` True, transport return value
   passed through, `error` None (no retry machinery engages).
3. `[erp_orders]` has `retry = 3` → attempt budget 3 + 1 = 4 (§7 convention). Four scripted
   transient failures exhaust the budget: `attempts == 4`, four transport invocations, failure
   type "transient".
4. Same endpoint, script T,T,success: retries stop at the first success → `attempts == 3`,
   result "ok3" (budget is a maximum, not a target).
5. Permanent failure on attempt 1: §6/§7 retries apply only to transient failures → exactly one
   transport call, `attempts == 1`, error `{"type": "permanent", "message": "bad request"}`
   (message = str of the raised exception).
6. `[notifier]` has `retry = 0` → budget 0 + 1 = 1: a transient failure is *not* retried;
   one call, one attempt.
7. `[marketing_sync]` has `retry = 2` (budget 3), but the second attempt raises
   PermanentError → the loop stops there: `attempts == 2`, type "permanent" (transient budget
   is irrelevant once a permanent failure occurs).
8. `[dw_accounts]` has `url = https://dw.example.internal/load/accounts`, `retry = 1`,
   `timeout_ms = 60000` → both attempts must call the transport with exactly that (url,
   60000) pair (config passed through on every attempt).
9. Negative expectation: neither error type may escape the wrapper — asserted by running a
   permanent script and an exhausting transient script inside try/except and failing on any
   exception.
10. The failure message is str() of the *last* raised exception: the scripted transport
    numbers its transient messages, so a retry=1 exhaustion ends with "timeout 2".
11. Result shape is exactly {ok, attempts, result, error} (target-spec rule 6).
12. On failure `result` is None (no partial payloads).
13. Security/scan expectation: no network/subprocess imports and no time.sleep (retries are
    immediate; determinism).

14. (added 2026-09-01 after mutation triage) Transient-exhaustion result shape: target-spec
    rule 6 fixes the exact four-key shape {ok, attempts, result, error} on *every* return
    path, and rule 12's "on failure result is None" applies to the transient-exhaustion
    path too. With retry = 1 (budget 2) and a transport that raises TransientError twice,
    the wrapper returns after attempt 2 with exactly those four keys and `result is None`.
    Closes the gap where only the success and permanent paths asserted the shape
    (surviving mutant: ERR-02 migrated.py node 109, 'result' -> 'result_X').
