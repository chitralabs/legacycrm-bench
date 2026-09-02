"""AUD-03 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def row(evt_id, ts="20260415103000", code="OPP_QUAL", usr="U0000006",
        ent="OPP_MASTER", ent_id="O00000025", old="P", new="W"):
    return {"EVT_ID": str(evt_id), "EVT_TS": ts, "EVT_CD": code, "USR_ID": usr,
            "ENT_NAME": ent, "ENT_ID": ent_id, "OLD_VAL": old, "NEW_VAL": new}


def test_timestamp_converted_to_iso8601(mod):
    assert mod.migrate_event(row(7, ts="20260415103000"))["ts"] == "2026-04-15T10:30:00"


def test_midnight_and_end_of_day_timestamps(mod):
    assert mod.migrate_event(row(1, ts="19991231235959"))["ts"] == "1999-12-31T23:59:59"
    assert mod.migrate_event(row(2, ts="20260101000000"))["ts"] == "2026-01-01T00:00:00"


def test_field_mapping_complete_and_exact(mod):
    e = mod.migrate_event(row(42))
    assert e == {"evt_id": 42, "ts": "2026-04-15T10:30:00", "code": "OPP_QUAL",
                 "user_id": "U0000006", "entity": "OPP_MASTER", "entity_id": "O00000025",
                 "old_val": "P", "new_val": "W"}


def test_empty_old_new_values_preserved(mod):
    e = mod.migrate_event(row(3, old="", new=""))
    assert e["old_val"] == "" and e["new_val"] == ""


def test_evt_id_is_int(mod):
    assert mod.migrate_event(row("0009"))["evt_id"] == 9


def test_migrate_orders_by_numeric_evt_id(mod):
    rows = [row(10), row(2), row(31), row(4)]  # deliberately shuffled; 31 > 4 numerically
    store = mod.migrate(rows)
    assert [e["evt_id"] for e in store.events()] == [2, 4, 10, 31]


def test_migrate_sample_rows_preserves_legacy_order(mod):
    sample = case_lib.read_csv(case_lib.legacy_root(__file__) / "aud_event_sample.csv")
    store = mod.migrate(list(reversed(sample)))
    assert [e["evt_id"] for e in store.events()] == sorted(int(r["EVT_ID"]) for r in sample)
    assert len(store) == len(sample)


def test_remigration_is_idempotent(mod):
    rows = [row(1), row(2), row(3)]
    store = mod.migrate(rows)
    store2 = mod.migrate(rows, store)
    assert store2 is store
    assert len(store) == 3


def test_overlapping_batch_adds_only_new_events(mod):
    store = mod.migrate([row(1), row(2)])
    mod.migrate([row(2), row(3)], store)
    assert [e["evt_id"] for e in store.events()] == [1, 2, 3]


def test_append_is_available_and_grows_store(mod):
    store = mod.migrate([row(1)])
    store.append(mod.migrate_event(row(99)))
    assert len(store) == 2
    assert store.events()[-1]["evt_id"] == 99


def test_store_exposes_no_update_or_delete_surface(mod):
    store = mod.migrate([row(1)])
    for name in ("update", "delete", "remove", "pop", "clear", "replace",
                 "__setitem__", "__delitem__"):
        assert not hasattr(store, name), f"append-only store must not expose {name}"


def test_events_returns_defensive_copy_of_list(mod):
    store = mod.migrate([row(1), row(2)])
    snapshot = store.events()
    snapshot.clear()
    assert len(store) == 2
    assert [e["evt_id"] for e in store.events()] == [1, 2]


def test_mutating_returned_event_does_not_alter_store(mod):
    store = mod.migrate([row(1)])
    store.events()[0]["new_val"] = "TAMPERED"
    assert store.events()[0]["new_val"] == "W"


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
