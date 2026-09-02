"""BIZ-02 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


USERS = [
    {"USR_ID": "U0000001", "USR_NM": "Sam Sales", "ROLE_ID": "SALES",
     "ACTIVE_FLG": "Y", "DEL_FLG": "N"},
    {"USR_ID": "U0000002", "USR_NM": "Mia Manager", "ROLE_ID": "MGR",
     "ACTIVE_FLG": "Y", "DEL_FLG": "N"},
    {"USR_ID": "U0000003", "USR_NM": "Ada Admin", "ROLE_ID": "ADMIN",
     "ACTIVE_FLG": "Y", "DEL_FLG": "N"},
    {"USR_ID": "U0000004", "USR_NM": "Gone Mgr", "ROLE_ID": "MGR",
     "ACTIVE_FLG": "Y", "DEL_FLG": "Y"},
    {"USR_ID": "U0000005", "USR_NM": "Idle Mgr", "ROLE_ID": "MGR",
     "ACTIVE_FLG": "N", "DEL_FLG": "N"},
]


def order(**over):
    row = {"ORD_ID": "D00000001", "ACCT_ID": "A00000001", "STAT_CD": "E",
           "DISC_PCT": 0, "TOT_AMT": "1000.00", "OWNER_UID": "U0000001",
           "DEL_FLG": "N"}
    row.update(over)
    return row


def test_small_discount_allowed_for_sales_role(mod):
    updated = mod.set_discount(order(), 10, "U0000001", USERS)
    assert updated["DISC_PCT"] == 10


def test_exactly_20_needs_no_role(mod):
    # Boundary: the legacy rule fires only when DISC_PCT > 20 (strict).
    updated = mod.set_discount(order(), 20, "U0000001", USERS)
    assert updated["DISC_PCT"] == 20


def test_20_point_01_rejected_for_sales_role(mod):
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.set_discount(order(), 20.01, "U0000001", USERS)
    assert exc.value.code == "E5002"


def test_20_point_01_allowed_for_mgr(mod):
    assert mod.set_discount(order(), 20.01, "U0000002", USERS)["DISC_PCT"] == 20.01


def test_20_point_01_allowed_for_admin(mod):
    assert mod.set_discount(order(), 20.01, "U0000003", USERS)["DISC_PCT"] == 20.01


def test_unknown_user_has_no_role(mod):
    # LOOKUP miss returns '' -> neither MGR nor ADMIN.
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.set_discount(order(), 25, "U0009999", USERS)
    assert exc.value.code == "E5002"


def test_soft_deleted_mgr_has_no_role(mod):
    # Negative: LOOKUP sees live rows only; a deleted MGR cannot authorize.
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.set_discount(order(), 25, "U0000004", USERS)
    assert exc.value.code == "E5002"


def test_soft_deleted_user_can_still_set_20(mod):
    # The role rule is not triggered at or below 20.
    assert mod.set_discount(order(), 20, "U0000004", USERS)["DISC_PCT"] == 20


def test_inactive_but_live_mgr_still_authorizes(mod):
    # ACTIVE_FLG is not part of LOOKUP semantics; only DEL_FLG matters.
    assert mod.set_discount(order(), 25, "U0000005", USERS)["DISC_PCT"] == 25


def test_negative_discount_out_of_range(mod):
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.set_discount(order(), -0.01, "U0000002", USERS)
    assert exc.value.code == "E5001"


def test_100_allowed_but_above_100_rejected(mod):
    assert mod.set_discount(order(), 100, "U0000002", USERS)["DISC_PCT"] == 100
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.set_discount(order(), 100.01, "U0000002", USERS)
    assert exc.value.code == "E5001"


def test_range_check_runs_before_role_check(mod):
    # Rule-file order: 150 by a SALES user reports E5001, not E5002.
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.set_discount(order(), 150, "U0000001", USERS)
    assert exc.value.code == "E5001"


def test_violation_messages_preserve_legacy_text(mod):
    with pytest.raises(mod.BusinessRuleViolation) as exc:
        mod.set_discount(order(), 21, "U0000001", USERS)
    assert exc.value.message == "Discount over 20 percent requires manager role"


def test_inputs_not_mutated(mod):
    o = order()
    snap_o = dict(o)
    snap_u = [dict(u) for u in USERS]
    mod.set_discount(o, 15, "U0000001", USERS)
    assert o == snap_o and USERS == snap_u
