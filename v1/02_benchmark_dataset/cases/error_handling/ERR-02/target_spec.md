# ERR-02 Target Specification

Migrate the legacy integration retry behavior (config: `legacy/endpoints.ini`; semantics:
`legacy/SEMANTICS_EXCERPT.md` = SYSTEM_OVERVIEW.md §6 with the §7 retry-count convention) to a
modern retry wrapper as **one Python module** `migrated.py`. Transport is **injected** so tests
are deterministic and networkless.

## Required interface

```python
class TransientError(Exception): ...   # retryable failure (timeout, 5xx, connection reset)
class PermanentError(Exception): ...   # non-retryable failure (4xx, bad payload, auth config)

def call_with_retry(endpoint_cfg: dict, transport) -> dict: ...
```

- `endpoint_cfg`: a parsed endpoints.ini section as a dict with at least
  `{"url": str, "retry": int, "timeout_ms": int}` (integers already parsed).
- `transport`: a callable `transport(url, timeout_ms)` supplied by the caller. It returns an
  arbitrary result object on success and raises `TransientError` or `PermanentError` (the
  classes exported by this module) on failure.

## Required behavior

1. **Attempt budget** (§7 convention applied to `retry`): the call is attempted at most
   `retry + 1` times — the initial attempt plus up to `retry` re-attempts.
2. **Only transient failures are retried.** A `TransientError` on a non-final attempt leads to
   another attempt; on the final attempt it produces the failure result.
3. **Permanent failures never retry**: a `PermanentError` stops immediately — the result
   reports exactly the attempts made so far (1 if it was the first attempt). A transient
   attempt followed by a permanent one stops at that permanent attempt.
4. **No exception propagates** to the caller for these two error types; the outcome is the
   returned dict.
5. `timeout_ms` and `url` from the config are passed to the transport on **every** attempt.
6. **Result shape** — exactly these keys:
   - `"ok"`: bool;
   - `"attempts"`: total number of transport invocations made (int ≥ 1);
   - `"result"`: the transport's return value on success, else `None`;
   - `"error"`: `None` on success, else `{"type": "transient"|"permanent",
     "message": str(<last raised exception>)}`.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no sleeping/backoff timing
  (retries are immediate), no network.
