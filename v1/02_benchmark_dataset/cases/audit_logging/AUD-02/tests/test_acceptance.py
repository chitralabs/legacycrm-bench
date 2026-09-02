"""AUD-02 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib

TS = "20260901120000"
USER = "U0000007"

EVENT_KEYS = {"EVT_TS", "EVT_CD", "USR_ID", "ENT_NAME", "ENT_ID", "OLD_VAL", "NEW_VAL"}


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def acct(**over):
    row = {"ACCT_ID": "A00000001", "ACCT_NM": "Aster Corp", "CRED_HOLD": "N",
           "CRED_LIMIT": "50000", "OWNER_UID": "U0000002", "TEAM_CD": "T01", "DEL_FLG": "N"}
    row.update(over)
    return row


def test_single_changed_audited_column_emits_one_event(mod):
    events = mod.emit_audits("ACCT_MASTER", acct(), acct(CRED_HOLD="Y"), USER, TS)
    assert events == [{"EVT_TS": TS, "EVT_CD": "COL_UPD", "USR_ID": USER,
                       "ENT_NAME": "ACCT_MASTER", "ENT_ID": "A00000001",
                       "OLD_VAL": "N", "NEW_VAL": "Y"}]


def test_multiple_changes_follow_config_file_order(mod):
    # OWNER_UID and CRED_HOLD both change; cfg order for ACCT_MASTER is
    # CRED_HOLD, CRED_LIMIT, OWNER_UID.
    events = mod.emit_audits("ACCT_MASTER", acct(),
                             acct(OWNER_UID="U0000005", CRED_HOLD="Y"), USER, TS)
    assert [(e["OLD_VAL"], e["NEW_VAL"]) for e in events] == [("N", "Y"),
                                                              ("U0000002", "U0000005")]


def test_unchanged_audited_columns_emit_nothing(mod):
    assert mod.emit_audits("ACCT_MASTER", acct(), acct(), USER, TS) == []


def test_changed_unaudited_column_emits_nothing(mod):
    # ACCT_NM is not in audit_config.cfg.
    assert mod.emit_audits("ACCT_MASTER", acct(), acct(ACCT_NM="Renamed"), USER, TS) == []


def test_unaudited_table_emits_nothing(mod):
    old = {"CONT_ID": "K00000001", "LAST_NM": "Old"}
    new = {"CONT_ID": "K00000001", "LAST_NM": "New"}
    assert mod.emit_audits("CONT_MASTER", old, new, USER, TS) == []


def test_numeric_values_are_stringified(mod):
    events = mod.emit_audits("ACCT_MASTER", acct(CRED_LIMIT=50000),
                             acct(CRED_LIMIT=75000), USER, TS)
    assert len(events) == 1
    assert events[0]["OLD_VAL"] == "50000" and events[0]["NEW_VAL"] == "75000"


def test_none_and_missing_stringify_to_empty(mod):
    old = {"OPP_ID": "O00000001", "STAT_CD": None}
    new = {"OPP_ID": "O00000001", "STAT_CD": "Q"}
    events = mod.emit_audits("OPP_MASTER", old, new, USER, TS)
    assert len(events) == 1
    assert events[0]["OLD_VAL"] == "" and events[0]["NEW_VAL"] == "Q"


def test_event_has_exactly_the_aud_event_field_names(mod):
    events = mod.emit_audits("ORD_HEADER",
                             {"ORD_ID": "D00000001", "STAT_CD": "E"},
                             {"ORD_ID": "D00000001", "STAT_CD": "A"}, USER, TS)
    assert len(events) == 1
    assert set(events[0].keys()) == EVENT_KEYS


def test_ent_id_uses_table_primary_key(mod):
    events = mod.emit_audits("CASE_MASTER",
                             {"CASE_ID": "C00000042", "SEV_CD": "3"},
                             {"CASE_ID": "C00000042", "SEV_CD": "1"}, USER, TS)
    assert events[0]["ENT_ID"] == "C00000042"
    events = mod.emit_audits("USR_MASTER",
                             {"USR_ID": "U0000009", "ROLE_ID": "REP"},
                             {"USR_ID": "U0000009", "ROLE_ID": "MGR"}, USER, TS)
    assert events[0]["ENT_ID"] == "U0000009"


def test_timestamp_and_user_pass_through_verbatim(mod):
    events = mod.emit_audits("USR_MASTER",
                             {"USR_ID": "U0000009", "ACTIVE_FLG": "Y"},
                             {"USR_ID": "U0000009", "ACTIVE_FLG": "N"}, "U0000042",
                             "19991231235959")
    assert events[0]["EVT_TS"] == "19991231235959"
    assert events[0]["USR_ID"] == "U0000042"


def test_mixed_changed_and_unchanged_only_changed_emit(mod):
    old = {"OPP_ID": "O00000002", "STAT_CD": "Q", "AMT": "1000", "OWNER_UID": "U0000002"}
    new = {"OPP_ID": "O00000002", "STAT_CD": "N", "AMT": "1000", "OWNER_UID": "U0000003"}
    events = mod.emit_audits("OPP_MASTER", old, new, USER, TS)
    # cfg order for OPP_MASTER: STAT_CD, AMT, OWNER_UID -> STAT_CD then OWNER_UID.
    assert [(e["OLD_VAL"], e["NEW_VAL"]) for e in events] == [("Q", "N"),
                                                              ("U0000002", "U0000003")]


def test_module_matches_legacy_config_for_every_table(mod):
    # Cross-check the baked-in config against the legacy artifact: flipping every column one at
    # a time must emit exactly for cfg-listed columns, in cfg file order.
    cfg = {}
    for raw in (case_lib.legacy_root(__file__) / "audit_config.cfg").read_text().splitlines():
        parts = raw.split()
        if len(parts) == 3 and parts[0] == "AUDIT":
            cfg.setdefault(parts[1], []).append(parts[2])
    pk = {"ACCT_MASTER": "ACCT_ID", "OPP_MASTER": "OPP_ID", "CASE_MASTER": "CASE_ID",
          "ORD_HEADER": "ORD_ID", "USR_MASTER": "USR_ID"}
    for table, columns in cfg.items():
        old = {pk[table]: "X00000001"}
        new = {pk[table]: "X00000001"}
        for i, col in enumerate(columns):
            old[col] = f"old{i}"
            new[col] = f"new{i}"
        old["UNAUDITED_X"] = "a"
        new["UNAUDITED_X"] = "b"
        events = mod.emit_audits(table, old, new, USER, TS)
        assert [e["OLD_VAL"] for e in events] == [f"old{i}" for i in range(len(columns))]


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
