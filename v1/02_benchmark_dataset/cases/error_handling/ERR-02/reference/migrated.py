"""ERR-02 reference solution: endpoint retry wrapper with injected transport.

SYSTEM_OVERVIEW.md §6/§7: retry counts additional attempts (initial + up to n re-attempts);
only transient failures are retried; permanent failures stop immediately; no exception
escapes for the two documented error types.
"""


class TransientError(Exception):
    """Retryable transport failure."""


class PermanentError(Exception):
    """Non-retryable transport failure."""


def call_with_retry(endpoint_cfg, transport):
    max_attempts = int(endpoint_cfg["retry"]) + 1
    url = endpoint_cfg["url"]
    timeout_ms = endpoint_cfg["timeout_ms"]
    attempts = 0
    while True:
        attempts += 1
        try:
            result = transport(url, timeout_ms)
        except TransientError as exc:
            if attempts >= max_attempts:
                return {"ok": False, "attempts": attempts, "result": None,
                        "error": {"type": "transient", "message": str(exc)}}
            continue
        except PermanentError as exc:
            return {"ok": False, "attempts": attempts, "result": None,
                    "error": {"type": "permanent", "message": str(exc)}}
        return {"ok": True, "attempts": attempts, "result": result, "error": None}
