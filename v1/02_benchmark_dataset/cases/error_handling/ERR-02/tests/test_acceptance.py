"""ERR-02 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import configparser
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


@pytest.fixture(scope="module")
def ini():
    cp = configparser.ConfigParser()
    cp.read_string((case_lib.legacy_root(__file__) / "endpoints.ini").read_text())
    return cp


def cfg_of(ini, section):
    return {"url": ini[section]["url"], "retry": int(ini[section]["retry"]),
            "timeout_ms": int(ini[section]["timeout_ms"])}


class Script:
    """Deterministic transport: raises/returns the scripted outcomes in order."""

    def __init__(self, mod, outcomes):
        self.mod = mod
        self.outcomes = list(outcomes)
        self.calls = []

    def __call__(self, url, timeout_ms):
        self.calls.append((url, timeout_ms))
        outcome = self.outcomes.pop(0)
        if outcome == "T":
            raise self.mod.TransientError(f"timeout {len(self.calls)}")
        if outcome == "P":
            raise self.mod.PermanentError("bad request")
        return outcome


def test_error_classes_exported(mod):
    assert issubclass(mod.TransientError, Exception)
    assert issubclass(mod.PermanentError, Exception)


def test_success_first_attempt(mod):
    t = Script(mod, ["payload-ok"])
    out = mod.call_with_retry({"url": "u", "retry": 3, "timeout_ms": 1000}, t)
    assert out == {"ok": True, "attempts": 1, "result": "payload-ok", "error": None}


def test_transient_exhaustion_uses_retry_plus_one_attempts(mod, ini):
    # erp_orders: retry = 3 -> exactly 4 attempts.
    t = Script(mod, ["T", "T", "T", "T"])
    out = mod.call_with_retry(cfg_of(ini, "erp_orders"), t)
    assert out["ok"] is False
    assert out["attempts"] == 4
    assert len(t.calls) == 4
    assert out["error"]["type"] == "transient"


def test_transient_then_success_stops_retrying(mod, ini):
    # erp_orders allows up to 4 attempts, but success on the 3rd ends the loop.
    t = Script(mod, ["T", "T", "ok3"])
    out = mod.call_with_retry(cfg_of(ini, "erp_orders"), t)
    assert out == {"ok": True, "attempts": 3, "result": "ok3", "error": None}


def test_permanent_error_never_retries(mod, ini):
    t = Script(mod, ["P"])
    out = mod.call_with_retry(cfg_of(ini, "erp_orders"), t)
    assert out["ok"] is False
    assert out["attempts"] == 1
    assert len(t.calls) == 1
    assert out["error"] == {"type": "permanent", "message": "bad request"}


def test_zero_retry_means_single_attempt(mod, ini):
    # notifier: retry = 0 -> one attempt even on transient failure.
    t = Script(mod, ["T"])
    out = mod.call_with_retry(cfg_of(ini, "notifier"), t)
    assert out["attempts"] == 1
    assert len(t.calls) == 1
    assert out["error"]["type"] == "transient"


def test_transient_then_permanent_stops_at_permanent(mod, ini):
    # marketing_sync: retry = 2 would allow 3 attempts, but attempt 2 is permanent.
    t = Script(mod, ["T", "P"])
    out = mod.call_with_retry(cfg_of(ini, "marketing_sync"), t)
    assert out["ok"] is False
    assert out["attempts"] == 2
    assert out["error"]["type"] == "permanent"


def test_timeout_and_url_passed_on_every_attempt(mod, ini):
    # dw_accounts: retry = 1, timeout_ms = 60000.
    t = Script(mod, ["T", "T"])
    mod.call_with_retry(cfg_of(ini, "dw_accounts"), t)
    assert t.calls == [("https://dw.example.internal/load/accounts", 60000)] * 2


def test_no_exception_propagates(mod):
    for outcomes in (["P"], ["T", "T"]):
        t = Script(mod, outcomes)
        try:
            mod.call_with_retry({"url": "u", "retry": 1, "timeout_ms": 5}, t)
        except Exception as exc:
            pytest.fail(f"wrapper must not raise, got {type(exc).__name__}")


def test_failure_message_is_last_error_str(mod):
    t = Script(mod, ["T", "T"])
    out = mod.call_with_retry({"url": "u", "retry": 1, "timeout_ms": 5}, t)
    assert out["error"]["message"] == "timeout 2"


def test_result_shape_keys_exact(mod):
    t = Script(mod, ["fine"])
    out = mod.call_with_retry({"url": "u", "retry": 0, "timeout_ms": 5}, t)
    assert set(out.keys()) == {"ok", "attempts", "result", "error"}


def test_failure_result_is_none(mod):
    t = Script(mod, ["P"])
    out = mod.call_with_retry({"url": "u", "retry": 0, "timeout_ms": 5}, t)
    assert out["result"] is None


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client", "time.sleep"):
        assert banned not in src
# --- Tests added 2026-09-01 after mutation triage (mutant_triage.md #6) ---

def test_transient_exhaustion_result_shape(mod):
    # Exhausting the transient budget must still return the exact four-key
    # shape with result None (previously only success/permanent paths checked).
    t = Script(mod, ["T", "T"])
    out = mod.call_with_retry({"url": "u", "retry": 1, "timeout_ms": 5}, t)
    assert set(out.keys()) == {"ok", "attempts", "result", "error"}
    assert out["result"] is None
