"""SCR-02 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def acct(acct_id="A00000001", **over):
    row = {"ACCT_ID": acct_id, "ACCT_NM": "Blue Harbor Ltd", "ACCT_TYP": "C",
           "CRED_LIMIT": "1000.00", "CRED_HOLD": "N", "CURR_CD": "", "DEL_FLG": "N"}
    row.update(over)
    return row


def inv(ord_id, tot, acct_id="A00000001", **over):
    row = {"ORD_ID": ord_id, "ACCT_ID": acct_id, "STAT_CD": "I",
           "TOT_AMT": tot, "DEL_FLG": "N"}
    row.update(over)
    return row


def test_hold_on_when_exposure_exceeds_limit(mod):
    accounts, audits = mod.sweep([acct()], [inv("O1", "700.00"), inv("O2", "500.00")])
    assert accounts[0]["CRED_HOLD"] == "Y"
    assert audits == [("CRED_HOLD_ON", "A00000001")]


def test_exposure_equal_to_limit_does_not_hold(mod):
    accounts, audits = mod.sweep([acct()], [inv("O1", "1000.00")])
    assert accounts[0]["CRED_HOLD"] == "N"
    assert audits == []


def test_held_account_in_hysteresis_band_stays_held(mod):
    accounts, audits = mod.sweep([acct(CRED_HOLD="Y")], [inv("O1", "900.00")])
    assert accounts[0]["CRED_HOLD"] == "Y"
    assert audits == []


def test_clear_account_in_hysteresis_band_stays_clear(mod):
    accounts, audits = mod.sweep([acct(CRED_HOLD="N")], [inv("O1", "900.00")])
    assert accounts[0]["CRED_HOLD"] == "N"
    assert audits == []


def test_release_at_exactly_eighty_percent(mod):
    accounts, audits = mod.sweep([acct(CRED_HOLD="Y")], [inv("O1", "800.00")])
    assert accounts[0]["CRED_HOLD"] == "N"
    assert audits == [("CRED_HOLD_OFF", "A00000001")]


def test_release_when_exposure_well_below_band(mod):
    accounts, audits = mod.sweep([acct(CRED_HOLD="Y")], [inv("O1", "100.00")])
    assert accounts[0]["CRED_HOLD"] == "N"
    assert audits == [("CRED_HOLD_OFF", "A00000001")]


def test_only_invoiced_orders_count_toward_exposure(mod):
    orders = [inv("O1", "300.00"), inv("O2", "2000.00", STAT_CD="S"),
              inv("O3", "900.00", STAT_CD="E")]
    accounts, audits = mod.sweep([acct()], orders)
    assert accounts[0]["CRED_HOLD"] == "N"
    assert audits == []


def test_soft_deleted_orders_excluded_from_exposure(mod):
    orders = [inv("O1", "300.00"), inv("O2", "2000.00", DEL_FLG="Y")]
    accounts, audits = mod.sweep([acct()], orders)
    assert accounts[0]["CRED_HOLD"] == "N"
    assert audits == []


def test_non_customer_and_soft_deleted_accounts_skipped(mod):
    accounts, audits = mod.sweep(
        [acct(ACCT_TYP="P", CRED_LIMIT="0"),
         acct(acct_id="A00000002", DEL_FLG="Y", CRED_LIMIT="0")],
        [inv("O1", "5000.00"), inv("O2", "5000.00", acct_id="A00000002")])
    assert accounts[0]["CRED_HOLD"] == "N"
    assert accounts[1]["CRED_HOLD"] == "N"
    assert audits == []


def test_blank_limit_defaults_to_zero(mod):
    accounts, audits = mod.sweep([acct(CRED_LIMIT="")], [inv("O1", "0.01")])
    assert accounts[0]["CRED_HOLD"] == "Y"
    assert audits == [("CRED_HOLD_ON", "A00000001")]


def test_zero_limit_held_account_with_no_exposure_released(mod):
    accounts, audits = mod.sweep([acct(CRED_LIMIT="0", CRED_HOLD="Y")], [])
    assert accounts[0]["CRED_HOLD"] == "N"
    assert audits == [("CRED_HOLD_OFF", "A00000001")]


def test_blank_hold_flag_counts_as_not_held(mod):
    accounts, audits = mod.sweep([acct(CRED_HOLD="")], [inv("O1", "1200.00")])
    assert accounts[0]["CRED_HOLD"] == "Y"
    assert audits == [("CRED_HOLD_ON", "A00000001")]


def test_audits_in_ascending_account_id_order(mod):
    accounts, audits = mod.sweep(
        [acct(acct_id="A00000009"), acct(acct_id="A00000002")],
        [inv("O1", "1500.00", acct_id="A00000009"),
         inv("O2", "1500.00", acct_id="A00000002")])
    assert audits == [("CRED_HOLD_ON", "A00000002"), ("CRED_HOLD_ON", "A00000009")]
    assert [a["ACCT_ID"] for a in accounts] == ["A00000009", "A00000002"]


def test_no_duplicate_hold_audit_for_already_held_account(mod):
    accounts, audits = mod.sweep([acct(CRED_HOLD="Y")], [inv("O1", "1200.00")])
    assert accounts[0]["CRED_HOLD"] == "Y"
    assert audits == []


def test_exposure_only_counts_own_orders(mod):
    accounts, audits = mod.sweep(
        [acct()], [inv("O1", "300.00"), inv("O2", "5000.00", acct_id="A00000099")])
    assert accounts[0]["CRED_HOLD"] == "N"
    assert audits == []


def test_inputs_not_mutated(mod):
    accts = [acct(CRED_HOLD="N")]
    orders = [inv("O1", "1500.00")]
    a_snap, o_snap = [dict(a) for a in accts], [dict(o) for o in orders]
    mod.sweep(accts, orders)
    assert accts == a_snap
    assert orders == o_snap


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
