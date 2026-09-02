"""CFG-02 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def test_to_iso_converts_normal_date(mod):
    assert mod.to_iso("20260901") == "2026-09-01"


def test_to_iso_sentinel_is_none(mod):
    assert mod.to_iso("00000000") is None


def test_to_iso_blank_and_none_are_none(mod):
    assert mod.to_iso("") is None
    assert mod.to_iso(None) is None


def test_from_iso_converts_normal_date(mod):
    assert mod.from_iso("2026-09-01") == "20260901"


def test_from_iso_none_is_sentinel(mod):
    assert mod.from_iso(None) == "00000000"


def test_legacy_round_trip(mod):
    for legacy in ("20240229", "19991231", "00000000"):
        assert mod.from_iso(mod.to_iso(legacy)) == legacy


def test_iso_round_trip(mod):
    assert mod.to_iso(mod.from_iso("2025-12-31")) == "2025-12-31"
    assert mod.to_iso(mod.from_iso(None)) is None


def test_yn_y_is_true(mod):
    assert mod.yn("Y") is True


def test_yn_everything_else_is_false(mod):
    assert mod.yn("N") is False
    assert mod.yn("") is False
    assert mod.yn(None) is False


def test_minor_units_usd(mod):
    out = mod.to_minor_units("1234.56", "USD")
    assert out == 123456
    assert isinstance(out, int)


def test_minor_units_blank_currency_defaults_to_usd(mod):
    assert mod.to_minor_units("1234.56", "") == 123456
    assert mod.to_minor_units("1234.56", None) == 123456


def test_minor_units_jpy_exponent_zero(mod):
    assert mod.to_minor_units("5000", "JPY") == 5000


def test_minor_units_half_up_rounding(mod):
    assert mod.to_minor_units("1234.5", "JPY") == 1235
    assert mod.to_minor_units("10.005", "USD") == 1001


def test_minor_units_decimal_safe_not_binary_float(mod):
    # 19.995 * 100 in binary floats is 1999.4999...; the decimal answer is 2000.
    assert mod.to_minor_units("19.995", "USD") == 2000


def test_minor_units_blank_amount_is_zero(mod):
    assert mod.to_minor_units("", "USD") == 0
    assert mod.to_minor_units(None, "JPY") == 0


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
