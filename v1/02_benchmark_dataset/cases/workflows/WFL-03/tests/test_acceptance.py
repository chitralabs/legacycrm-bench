"""WFL-03 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def order(**over):
    rec = {"ORD_ID": "O00000001", "ACCT_ID": "A00000001", "STAT_CD": "E",
           "TOT_AMT": "250.00", "DISC_PCT": "0", "ORD_DT": "20260810", "DEL_FLG": "N"}
    rec.update(over)
    return rec


def acct(**over):
    row = {"ACCT_ID": "A00000001", "ACCT_NM": "Blue Harbor Ltd", "ACCT_TYP": "C",
           "CRED_HOLD": "N", "CRED_LIMIT": "10000.00", "DEL_FLG": "N"}
    row.update(over)
    return row


def tables(*accounts):
    return {"ACCT_MASTER": list(accounts)}


def test_approve_with_positive_total(mod):
    res = mod.fire("E", "approve", order(TOT_AMT="250.00"), tables(acct()))
    assert res["state"] == "A"
    assert res["audits"] == ["ORD_APPR"]
    assert res["matched"] is True


def test_approve_zero_total_is_nomatch(mod):
    res = mod.fire("E", "approve", order(TOT_AMT="0"), tables(acct()))
    assert res["state"] == "E"
    assert res["audits"] == ["WF_NOMATCH"]
    assert res["matched"] is False


def test_approve_empty_total_coerces_to_zero(mod):
    res = mod.fire("E", "approve", order(TOT_AMT=""), tables(acct()))
    assert res["matched"] is False
    assert res["audits"] == ["WF_NOMATCH"]


def test_ship_emits_audit_and_notify(mod):
    res = mod.fire("A", "ship", order(STAT_CD="A"), tables(acct()))
    assert res["state"] == "S"
    assert res["audits"] == ["ORD_SHIP"]
    assert res["notifies"] == ["shipped"]


def test_invoice_from_shipped(mod):
    res = mod.fire("S", "invoice", order(STAT_CD="S"), tables(acct()))
    assert res["state"] == "I"
    assert res["audits"] == ["ORD_INV"]
    assert res["notifies"] == []


def test_cancel_entered_order_is_unguarded(mod):
    res = mod.fire("E", "cancel", order(), tables(acct(CRED_HOLD="Y")))
    assert res["state"] == "X"
    assert res["audits"] == ["ORD_CANC"]


def test_cancel_approved_order_without_credit_hold(mod):
    res = mod.fire("A", "cancel", order(STAT_CD="A"), tables(acct(CRED_HOLD="N")))
    assert res["state"] == "X"
    assert res["audits"] == ["ORD_CANC"]
    assert res["notifies"] == []


def test_cancel_approved_order_blocked_by_credit_hold(mod):
    res = mod.fire("A", "cancel", order(STAT_CD="A"), tables(acct(CRED_HOLD="Y")))
    assert res["state"] == "A"
    assert res["audits"] == ["WF_NOMATCH"]
    assert res["matched"] is False
    assert "ORD_CANC" not in res["audits"]
    assert res["notifies"] == []


def test_cancel_approved_order_with_missing_account_is_allowed(mod):
    res = mod.fire("A", "cancel", order(STAT_CD="A", ACCT_ID="A99999999"),
                   tables(acct(CRED_HOLD="Y")))
    assert res["state"] == "X"
    assert res["audits"] == ["ORD_CANC"]


def test_cancel_with_soft_deleted_held_account_is_allowed(mod):
    res = mod.fire("A", "cancel", order(STAT_CD="A"),
                   tables(acct(CRED_HOLD="Y", DEL_FLG="Y")))
    assert res["state"] == "X"
    assert res["audits"] == ["ORD_CANC"]
    assert res["matched"] is True


def test_cancel_invoiced_order_fires_invoiced_row_not_plain_cancel(mod):
    res = mod.fire("I", "cancel", order(STAT_CD="I"), tables(acct(CRED_HOLD="Y")))
    assert res["state"] == "X"
    assert res["audits"] == ["ORD_CANC_INV"]
    assert "ORD_CANC" not in res["audits"]
    assert res["notifies"] == ["credit_note"]


def test_cancel_shipped_order_is_nomatch(mod):
    res = mod.fire("S", "cancel", order(STAT_CD="S"), tables(acct()))
    assert res["state"] == "S"
    assert res["audits"] == ["WF_NOMATCH"]
    assert res["matched"] is False


def test_cancel_terminal_state_is_nomatch(mod):
    res = mod.fire("X", "cancel", order(STAT_CD="X"), tables(acct()))
    assert res["state"] == "X"
    assert res["matched"] is False


def test_lookup_keys_on_the_records_account(mod):
    held = acct(ACCT_ID="A00000001", CRED_HOLD="Y")
    clear = acct(ACCT_ID="A00000002", CRED_HOLD="N")
    tbl = tables(held, clear)
    blocked = mod.fire("A", "cancel", order(STAT_CD="A", ACCT_ID="A00000001"), tbl)
    allowed = mod.fire("A", "cancel", order(STAT_CD="A", ACCT_ID="A00000002"), tbl)
    assert blocked["matched"] is False
    assert allowed["matched"] is True
    assert allowed["audits"] == ["ORD_CANC"]


def test_inputs_not_mutated(mod):
    rec = order(STAT_CD="A")
    tbl = tables(acct(CRED_HOLD="N"))
    rec_snap = dict(rec)
    tbl_snap = [dict(r) for r in tbl["ACCT_MASTER"]]
    mod.fire("A", "cancel", rec, tbl)
    assert rec == rec_snap
    assert tbl["ACCT_MASTER"] == tbl_snap


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
# --- Tests added 2026-09-01 after mutation triage (mutant_triage.md #28) ---

def test_matched_fire_returns_exact_key_set_and_unchanged_record(mod):
    # Spec: result has exactly the keys state/record/audits/notifies/matched.
    # approve (E->A) has no <set> actions, so the returned record equals the input.
    res = mod.fire("E", "approve", order(), tables(acct()))
    assert set(res.keys()) == {"state", "record", "audits", "notifies", "matched"}
    assert res["record"] == order()
