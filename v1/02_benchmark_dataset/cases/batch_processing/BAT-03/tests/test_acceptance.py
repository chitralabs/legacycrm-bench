"""BAT-03 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def rows(n):
    return [f"REC{i:05d}" for i in range(n)]


def run(mod, n):
    payloads = []
    returned = mod.export_chunks(rows(n), payloads.append)
    return returned, payloads


def records(payload):
    parts = payload.split("\n")
    assert parts[-1] == ""  # trailing newline after the last record
    return parts[:-1]


def test_zero_rows_sends_nothing(mod):
    returned, payloads = run(mod, 0)
    assert payloads == []
    assert returned == 0


def test_single_row_payload(mod):
    returned, payloads = run(mod, 1)
    assert payloads == ["REC00000\n"]
    assert returned == 1


def test_499_rows_single_partial_chunk(mod):
    returned, payloads = run(mod, 499)
    assert len(payloads) == 1
    assert len(records(payloads[0])) == 499
    assert returned == 499


def test_500_rows_exactly_one_full_chunk(mod):
    returned, payloads = run(mod, 500)
    assert len(payloads) == 1
    assert returned == 500


def test_500_rows_payload_contents(mod):
    _, payloads = run(mod, 500)
    recs = records(payloads[0])
    assert len(recs) == 500
    assert recs[0] == "REC00000"
    assert recs[-1] == "REC00499"


def test_501_rows_full_chunk_plus_remainder(mod):
    returned, payloads = run(mod, 501)
    assert [len(records(p)) for p in payloads] == [500, 1]
    assert returned == 501


def test_501_rows_chunk_boundary_contents(mod):
    _, payloads = run(mod, 501)
    assert records(payloads[0])[-1] == "REC00499"
    assert records(payloads[1]) == ["REC00500"]


def test_1000_rows_two_chunks_no_trailing_empty_send(mod):
    returned, payloads = run(mod, 1000)
    assert [len(records(p)) for p in payloads] == [500, 500]
    assert returned == 1000


def test_every_record_followed_by_newline(mod):
    _, payloads = run(mod, 501)
    for p in payloads:
        assert p.endswith("\n")
        assert p == "".join(r + "\n" for r in records(p))


def test_no_empty_payload_is_ever_sent(mod):
    for n in (0, 1, 499, 500, 501, 1000):
        _, payloads = run(mod, n)
        assert all(p != "" for p in payloads)


def test_concatenated_chunks_reproduce_input_order(mod):
    _, payloads = run(mod, 1000)
    combined = [r for p in payloads for r in records(p)]
    assert combined == rows(1000)


def test_return_value_counts_all_records_sent(mod):
    for n in (1, 499, 500, 501, 1000):
        returned, _ = run(mod, n)
        assert returned == n


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
