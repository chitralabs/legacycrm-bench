"""ERR-01 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def test_normal_division(mod):
    assert mod.safe_div(10, 4) == (2.5, [])


def test_division_by_zero_yields_zero_and_audit(mod):
    value, audits = mod.safe_div(7, 0)
    assert value == 0.0
    assert audits == ["SCRIPT_DIV0"]


def test_zero_over_zero_is_quirk_not_nan(mod):
    value, audits = mod.safe_div(0, 0)
    assert value == 0.0 and value == value  # not NaN
    assert audits == ["SCRIPT_DIV0"]


def test_no_exception_propagates_on_zero_divisor(mod):
    try:
        mod.safe_div(1, 0)
        mod.safe_div(1, "")
        mod.safe_div(1, None)
        mod.safe_div(1, "0")
    except Exception as exc:  # pragma: no cover - the assertion message is the point
        pytest.fail(f"legacy quirk must not raise, got {type(exc).__name__}")


def test_empty_string_numerator_coerces_to_zero(mod):
    assert mod.safe_div("", 5) == (0.0, [])


def test_empty_string_divisor_is_div0(mod):
    value, audits = mod.safe_div(5, "")
    assert value == 0.0
    assert audits == ["SCRIPT_DIV0"]


def test_none_divisor_is_div0(mod):
    value, audits = mod.safe_div(5, None)
    assert value == 0.0
    assert audits == ["SCRIPT_DIV0"]


def test_numeric_string_operands(mod):
    assert mod.safe_div("9", "3") == (3.0, [])


def test_string_zero_divisor_is_div0(mod):
    value, audits = mod.safe_div("9", "0")
    assert value == 0.0
    assert audits == ["SCRIPT_DIV0"]


def test_no_audit_on_successful_division(mod):
    _, audits = mod.safe_div(100, 8)
    assert audits == []


def test_div0_result_is_number_zero_not_none(mod):
    value, _ = mod.safe_div(3, 0)
    assert value == 0
    assert value is not None
    assert isinstance(value, (int, float))


def test_negative_operands(mod):
    assert mod.safe_div(-9, 3) == (-3.0, [])
    assert mod.safe_div(9, -3) == (-3.0, [])


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
