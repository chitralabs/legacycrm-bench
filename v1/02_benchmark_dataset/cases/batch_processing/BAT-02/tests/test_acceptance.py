"""BAT-02 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def job(name, policy="ABORT", retries=0, at="01:00"):
    return {"name": name, "at": at, "script": name + ".crms",
            "on_error": {"policy": policy, "retries": retries}}


class ScriptedExecutor:
    """Deterministic executor: fails a job while its remaining fail-count is > 0."""

    def __init__(self, fail_counts=None):
        self.fail_counts = dict(fail_counts or {})
        self.calls = []

    def __call__(self, j):
        name = j["name"]
        self.calls.append(name)
        remaining = self.fail_counts.get(name, 0)
        if remaining > 0:
            self.fail_counts[name] = remaining - 1
            raise RuntimeError(f"{name} failed")


def test_all_jobs_succeed_in_order(mod):
    ex = ScriptedExecutor()
    log = mod.run_jobs([job("a"), job("b"), job("c")], ex)
    assert [e["name"] for e in log] == ["a", "b", "c"]
    assert all(e["outcome"] == "ok" and e["attempts"] == 1 and e["audits"] == []
               for e in log)
    assert ex.calls == ["a", "b", "c"]


def test_abort_failure_stops_the_schedule(mod):
    ex = ScriptedExecutor({"b": 1})
    log = mod.run_jobs([job("a"), job("b", "ABORT"), job("c")], ex)
    assert [e["name"] for e in log] == ["a", "b"]
    assert log[1] == {"name": "b", "attempts": 1, "outcome": "abort", "audits": []}


def test_no_executor_calls_after_abort(mod):
    ex = ScriptedExecutor({"b": 1})
    mod.run_jobs([job("a"), job("b", "ABORT"), job("c"), job("d")], ex)
    assert "c" not in ex.calls
    assert "d" not in ex.calls


def test_continue_failure_logs_rowskip_and_proceeds(mod):
    ex = ScriptedExecutor({"a": 1})
    log = mod.run_jobs([job("a", "CONTINUE"), job("b")], ex)
    assert log[0] == {"name": "a", "attempts": 1, "outcome": "skip",
                      "audits": ["BATCH_ROWSKIP"]}
    assert log[1]["name"] == "b"
    assert log[1]["outcome"] == "ok"


def test_retry_succeeds_after_two_failures(mod):
    ex = ScriptedExecutor({"a": 2})
    log = mod.run_jobs([job("a", "RETRY", 2), job("b")], ex)
    assert log[0] == {"name": "a", "attempts": 3, "outcome": "ok", "audits": []}
    assert log[1]["outcome"] == "ok"


def test_retry_exhausted_aborts_schedule(mod):
    ex = ScriptedExecutor({"a": 99})
    log = mod.run_jobs([job("a", "RETRY", 2), job("b")], ex)
    assert log == [{"name": "a", "attempts": 3, "outcome": "abort", "audits": []}]
    assert "b" not in ex.calls


def test_retry_job_succeeding_first_time_makes_one_attempt(mod):
    ex = ScriptedExecutor()
    log = mod.run_jobs([job("a", "RETRY", 2)], ex)
    assert log[0]["attempts"] == 1
    assert log[0]["outcome"] == "ok"
    assert ex.calls == ["a"]


def test_retry_one_failing_both_attempts(mod):
    ex = ScriptedExecutor({"a": 99})
    log = mod.run_jobs([job("a", "RETRY", 1)], ex)
    assert log[0]["attempts"] == 2
    assert log[0]["outcome"] == "abort"


def test_multiple_continue_failures_all_skipped(mod):
    ex = ScriptedExecutor({"a": 1, "b": 1})
    log = mod.run_jobs([job("a", "CONTINUE"), job("b", "CONTINUE"), job("c")], ex)
    assert [e["outcome"] for e in log] == ["skip", "skip", "ok"]
    assert [e["audits"] for e in log] == [["BATCH_ROWSKIP"], ["BATCH_ROWSKIP"], []]


def test_successful_continue_job_logs_no_rowskip(mod):
    ex = ScriptedExecutor()
    log = mod.run_jobs([job("a", "CONTINUE")], ex)
    assert log[0]["audits"] == []
    assert log[0]["outcome"] == "ok"


def test_attempts_equal_executor_invocations(mod):
    ex = ScriptedExecutor({"a": 1})
    log = mod.run_jobs([job("a", "RETRY", 3), job("b")], ex)
    assert log[0]["attempts"] == ex.calls.count("a") == 2
    assert log[1]["attempts"] == ex.calls.count("b") == 1


def test_runner_does_not_propagate_job_exceptions(mod):
    ex = ScriptedExecutor({"a": 1})
    log = mod.run_jobs([job("a", "ABORT")], ex)  # must not raise
    assert log[0]["outcome"] == "abort"


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client",
                   "time.sleep"):
        assert banned not in src
