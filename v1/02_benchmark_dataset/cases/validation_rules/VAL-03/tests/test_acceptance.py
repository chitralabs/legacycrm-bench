"""VAL-03 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def codes(errors):
    return [e["code"] for e in errors]


def tables():
    return {
        "USR_MASTER": [
            {"USR_ID": "U0000001", "USR_NM": "Mira Okafor", "ROLE_ID": "MGR",
             "TEAM_CD": "T01", "ACTIVE_FLG": "Y", "DEL_FLG": "N"},
            {"USR_ID": "U0000002", "USR_NM": "Jon Petrov", "ROLE_ID": "SLS",
             "TEAM_CD": "T01", "ACTIVE_FLG": "Y", "DEL_FLG": "N"},
            {"USR_ID": "U0000003", "USR_NM": "Lea Fontaine", "ROLE_ID": "MGR",
             "TEAM_CD": "T02", "ACTIVE_FLG": "Y", "DEL_FLG": "Y"},
            {"USR_ID": "U0000004", "USR_NM": "Sam Idris", "ROLE_ID": "ADMIN",
             "TEAM_CD": "T02", "ACTIVE_FLG": "Y", "DEL_FLG": "N"},
        ],
        "PROD_MASTER": [
            {"PROD_ID": "P00000001", "PROD_NM": "Gasket Kit", "ACTIVE_FLG": "Y",
             "DEL_FLG": "N"},
            {"PROD_ID": "P00000002", "PROD_NM": "Legacy Valve", "ACTIVE_FLG": "N",
             "DEL_FLG": "N"},
            {"PROD_ID": "P00000003", "PROD_NM": "Retired Pump", "ACTIVE_FLG": "Y",
             "DEL_FLG": "Y"},
        ],
    }


def header(**over):
    rec = {"ORD_ID": "D00000001", "ACCT_ID": "A00000001", "ORD_DT": "20260810",
           "STAT_CD": "E", "CURR_CD": "", "DISC_PCT": 10, "TOT_AMT": 1000,
           "OWNER_UID": "U0000002", "DEL_FLG": "N"}
    rec.update(over)
    return rec


def line(**over):
    rec = {"ORD_ID": "D00000001", "LINE_NO": 1, "PROD_ID": "P00000001",
           "QTY": 3, "UNIT_PRC": 25, "EXT_AMT": 75, "DEL_FLG": "N"}
    rec.update(over)
    return rec


def test_compliant_header_insert_returns_empty(mod):
    assert mod.validate(header(), None, "INSERT", tables(), "ORD_HEADER") == []


def test_discount_out_of_range_blocked_both_directions(mod):
    high = mod.validate(header(DISC_PCT=101), None, "INSERT", tables(), "ORD_HEADER")
    low = mod.validate(header(DISC_PCT=-1), None, "INSERT", tables(), "ORD_HEADER")
    assert codes(high) == ["E5001"]
    assert codes(low) == ["E5001"]
    assert mod.is_blocked(high) is True


def test_blank_discount_coerces_to_zero_and_passes(mod):
    assert mod.validate(header(DISC_PCT=""), header(), "UPDATE", tables(), "ORD_HEADER") == []


def test_high_discount_allowed_for_manager_owner(mod):
    rec = header(DISC_PCT=25, OWNER_UID="U0000001")
    assert mod.validate(rec, header(), "UPDATE", tables(), "ORD_HEADER") == []


def test_high_discount_allowed_for_admin_owner(mod):
    rec = header(DISC_PCT=25, OWNER_UID="U0000004")
    assert mod.validate(rec, header(), "UPDATE", tables(), "ORD_HEADER") == []


def test_high_discount_blocked_for_sales_owner(mod):
    rec = header(DISC_PCT=25, OWNER_UID="U0000002")
    assert codes(mod.validate(rec, header(), "UPDATE", tables(), "ORD_HEADER")) == ["E5002"]


def test_high_discount_blocked_for_unknown_owner(mod):
    rec = header(DISC_PCT=25, OWNER_UID="U0000099")
    assert codes(mod.validate(rec, header(), "UPDATE", tables(), "ORD_HEADER")) == ["E5002"]


def test_high_discount_blocked_for_soft_deleted_manager(mod):
    rec = header(DISC_PCT=25, OWNER_UID="U0000003")  # MGR row but DEL_FLG='Y'
    assert codes(mod.validate(rec, header(), "UPDATE", tables(), "ORD_HEADER")) == ["E5002"]


def test_discount_exactly_twenty_needs_no_manager(mod):
    rec = header(DISC_PCT=20, OWNER_UID="U0000002")
    assert mod.validate(rec, header(), "UPDATE", tables(), "ORD_HEADER") == []


def test_discount_rule_not_fired_on_insert(mod):
    rec = header(DISC_PCT=25, OWNER_UID="U0000002")
    assert "E5002" not in codes(mod.validate(rec, None, "INSERT", tables(), "ORD_HEADER"))


def test_invoiced_order_cannot_move_to_shipped(mod):
    old = header(STAT_CD="I")
    new = header(STAT_CD="S")
    assert codes(mod.validate(new, old, "UPDATE", tables(), "ORD_HEADER")) == ["E5003"]


def test_invoiced_order_may_be_cancelled_or_stay(mod):
    old = header(STAT_CD="I")
    assert mod.validate(header(STAT_CD="X"), old, "UPDATE", tables(), "ORD_HEADER") == []
    assert mod.validate(header(STAT_CD="I"), old, "UPDATE", tables(), "ORD_HEADER") == []


def test_zero_quantity_line_blocked(mod):
    assert codes(mod.validate(line(QTY=0), None, "INSERT", tables(), "ORD_LINE")) == ["E5004"]


def test_live_active_product_line_passes(mod):
    assert mod.validate(line(), None, "INSERT", tables(), "ORD_LINE") == []


def test_inactive_product_blocked(mod):
    rec = line(PROD_ID="P00000002")
    assert codes(mod.validate(rec, None, "INSERT", tables(), "ORD_LINE")) == ["E5005"]


def test_soft_deleted_product_blocked(mod):
    rec = line(PROD_ID="P00000003")  # ACTIVE_FLG='Y' but soft-deleted -> LOOKUP miss
    assert codes(mod.validate(rec, None, "INSERT", tables(), "ORD_LINE")) == ["E5005"]


def test_missing_product_blocked(mod):
    rec = line(PROD_ID="P00000099")
    assert codes(mod.validate(rec, None, "INSERT", tables(), "ORD_LINE")) == ["E5005"]


def test_product_rule_not_fired_on_update(mod):
    rec = line(PROD_ID="P00000099", QTY=5)
    assert mod.validate(rec, line(), "UPDATE", tables(), "ORD_LINE") == []


def test_line_failures_collected_in_file_order(mod):
    rec = line(QTY=0, PROD_ID="P00000002")
    assert codes(mod.validate(rec, None, "INSERT", tables(), "ORD_LINE")) == ["E5004", "E5005"]


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
# --- Tests added 2026-09-01 after mutation triage (mutant_triage.md #24, #25) ---

def test_default_event_is_insert_for_product_rule(mod):
    # target_spec fixes the signature default event="INSERT"; calling without an
    # event must still run the INSERT-only ORD-005 product-active LOOKUP.
    errs = mod.validate(line(PROD_ID="P00000002"), tables=tables(), table="ORD_LINE")
    assert codes(errs) == ["E5005"]


def test_discount_boundary_100_inclusive(mod):
    # ORD-001 is inclusive: DISC_PCT <= 100, so exactly 100 is legal.
    assert mod.validate(header(DISC_PCT=100), None, "INSERT", tables(), "ORD_HEADER") == []
