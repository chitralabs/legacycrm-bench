"""INT-02 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def acct(**over):
    row = {"ACCT_ID": "A00000001", "ACCT_NM": "Acme Industrial Group",
           "ACCT_TYP": "C", "REGION_CD": "NAM", "ANN_REV": "2500000.50",
           "CURR_CD": "", "CRED_HOLD": "Y", "CREATE_DT": "20190215",
           "DEL_FLG": "N"}
    row.update(over)
    return row


def test_record_is_exactly_77_chars(mod):
    assert len(mod.format_account(acct())) == 77


def test_acct_id_field_left_aligned_space_padded(mod):
    assert mod.format_account(acct())[0:10] == "A00000001 "


def test_name_field_left_aligned_space_padded_to_40(mod):
    assert mod.format_account(acct())[10:50] == "Acme Industrial Group" + " " * 19


def test_name_truncated_at_exactly_40(mod):
    long_name = "X" * 39 + "Y" + "OVERFLOW"  # 48 chars; char 40 is 'Y'
    rec = mod.format_account(acct(ACCT_NM=long_name))
    assert rec[10:50] == "X" * 39 + "Y"
    assert len(rec) == 77
    assert "OVERFLOW" not in rec  # negative: nothing beyond width 40 leaks


def test_region_field_slice(mod):
    assert mod.format_account(acct())[50:53] == "NAM"


def test_blank_region_is_three_spaces(mod):
    assert mod.format_account(acct(REGION_CD=""))[50:53] == "   "


def test_ann_rev_as_zero_padded_integer_cents(mod):
    assert mod.format_account(acct())[53:68] == "000000250000050"


def test_blank_ann_rev_is_zero_cents(mod):
    assert mod.format_account(acct(ANN_REV=""))[53:68] == "0" * 15


def test_ann_rev_rounded_half_up_to_integer_cents(mod):
    # 999.995 * 100 = 99999.5 cents -> half-up -> 100000
    assert mod.format_account(acct(ANN_REV="999.995"))[53:68] == "000000000100000"


def test_cred_hold_y_preserved(mod):
    assert mod.format_account(acct())[68] == "Y"


def test_blank_cred_hold_written_as_N(mod):
    assert mod.format_account(acct(CRED_HOLD=""))[68] == "N"


def test_create_dt_field_slice(mod):
    assert mod.format_account(acct())[69:77] == "20190215"


def test_missing_create_dt_written_as_sentinel(mod):
    assert mod.format_account(acct(CREATE_DT=""))[69:77] == "00000000"


def test_whole_record_exact(mod):
    expected = ("A00000001 "
                + "Acme Industrial Group" + " " * 19
                + "NAM"
                + "000000250000050"
                + "Y"
                + "20190215")
    assert mod.format_account(acct()) == expected


def test_no_record_terminator_appended(mod):
    assert not mod.format_account(acct()).endswith("\n")


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
# --- Tests added 2026-09-01 after mutation triage (mutant_triage.md #7) ---

def test_record_width_77_with_blank_create_dt(mod):
    # The sentinel-date path must also produce exactly 77 chars: the record is
    # 69 chars of earlier fields + the 8-char '00000000' sentinel, nothing more.
    assert len(mod.format_account(acct(CREATE_DT=""))) == 77
