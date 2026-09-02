"""BAT-01 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import json
import pytest
import case_lib

EXPECTED_NAMES = ["integrity_check", "credit_hold_sweep", "order_totals",
                  "case_escalation", "dw_export"]


@pytest.fixture(scope="module")
def sched():
    path = case_lib.solution_file(__file__, "schedule.json")
    return json.loads(path.read_text())


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def test_five_jobs_in_file_order(sched):
    assert [j["name"] for j in sched] == EXPECTED_NAMES


def test_schedule_times(sched):
    assert [j["at"] for j in sched] == ["01:00", "01:30", "02:00", "02:30", "03:00"]


def test_scripts(sched):
    assert [j["script"] for j in sched] == [n + ".crms" for n in EXPECTED_NAMES]


def test_on_error_policies(sched):
    assert [j["on_error"]["policy"] for j in sched] == \
        ["CONTINUE", "ABORT", "RETRY", "CONTINUE", "RETRY"]


def test_retry_counts_are_integers(sched):
    retries = [j["on_error"]["retries"] for j in sched]
    assert retries == [0, 0, 2, 0, 1]
    assert all(isinstance(r, int) and not isinstance(r, bool) for r in retries)


def test_entry_schema_has_exact_keys(sched):
    for j in sched:
        assert set(j.keys()) == {"name", "at", "script", "on_error"}
        assert set(j["on_error"].keys()) == {"policy", "retries"}


def test_no_invented_or_duplicate_jobs(sched):
    names = [j["name"] for j in sched]
    assert sorted(names) == sorted(EXPECTED_NAMES)
    assert len(names) == len(set(names))


def test_parser_defaults_absent_on_error_to_abort(mod):
    jobs = mod.parse_schedule("JOB reindex AT 04:00 RUN reindex.crms\n")
    assert jobs == [{"name": "reindex", "at": "04:00", "script": "reindex.crms",
                     "on_error": {"policy": "ABORT", "retries": 0}}]


def test_parser_reads_retry_clause(mod):
    jobs = mod.parse_schedule("JOB sync AT 05:15 RUN sync.crms ON_ERROR RETRY:3\n")
    assert jobs[0]["on_error"] == {"policy": "RETRY", "retries": 3}


def test_parser_skips_comments_and_blank_lines(mod):
    text = "# nightly schedule\n\nJOB one AT 01:00 RUN one.crms ON_ERROR CONTINUE\n"
    jobs = mod.parse_schedule(text)
    assert len(jobs) == 1
    assert jobs[0]["name"] == "one"


def test_parser_preserves_file_order(mod):
    text = ("JOB b AT 02:00 RUN b.crms\n"
            "JOB a AT 01:00 RUN a.crms\n")
    assert [j["name"] for j in mod.parse_schedule(text)] == ["b", "a"]


def test_parser_output_matches_shipped_schedule_json(mod, sched):
    cfg = (case_lib.legacy_root(__file__) / "batch_jobs.cfg").read_text()
    assert mod.parse_schedule(cfg) == sched


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
