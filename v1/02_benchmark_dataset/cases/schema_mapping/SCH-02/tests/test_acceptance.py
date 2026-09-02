"""SCH-02 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib

MODERN_KEYS = {
    "contact_id", "account_id", "first_name", "last_name", "email", "phone",
    "preferred_channel", "marketing_optout", "owner_id", "team_code", "created_date",
}


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def legacy_row(**over):
    row = {"CONT_ID": "K00000001", "ACCT_ID": "A00000001", "FRST_NM": "Dana",
           "LAST_NM": "Whitfield", "EMAIL_TX": "dana.whitfield@example.com",
           "PHONE_TX": "+1-555-0142", "PREF_CH": "E", "OPTOUT_FLG": "N",
           "OWNER_UID": "U0000001", "TEAM_CD": "T02", "CREATE_DT": "20230605",
           "DEL_FLG": "N"}
    row.update(over)
    return row


def test_soft_deleted_contact_returns_none(mod):
    assert mod.convert_contact(legacy_row(DEL_FLG="Y")) is None


def test_output_has_exactly_the_modern_keys(mod):
    out = mod.convert_contact(legacy_row())
    assert set(out.keys()) == MODERN_KEYS


def test_no_legacy_keys_leak_into_output(mod):
    out = mod.convert_contact(legacy_row())
    for legacy_key in ("CONT_ID", "EMAIL_TX", "PREF_CH", "OPTOUT_FLG", "DEL_FLG"):
        assert legacy_key not in out


def test_pref_channel_codes_map_to_enum(mod):
    assert mod.convert_contact(legacy_row(PREF_CH="E"))["preferred_channel"] == "email"
    assert mod.convert_contact(legacy_row(PREF_CH="P"))["preferred_channel"] == "phone"
    assert mod.convert_contact(legacy_row(PREF_CH="M"))["preferred_channel"] == "mail"


def test_blank_pref_channel_defaults_to_email(mod):
    assert mod.convert_contact(legacy_row(PREF_CH=""))["preferred_channel"] == "email"


def test_optout_y_is_true(mod):
    assert mod.convert_contact(legacy_row(OPTOUT_FLG="Y"))["marketing_optout"] is True


def test_optout_n_and_blank_are_false(mod):
    assert mod.convert_contact(legacy_row(OPTOUT_FLG="N"))["marketing_optout"] is False
    assert mod.convert_contact(legacy_row(OPTOUT_FLG=""))["marketing_optout"] is False


def test_blank_email_becomes_none(mod):
    assert mod.convert_contact(legacy_row(EMAIL_TX=""))["email"] is None


def test_nonblank_email_preserved(mod):
    out = mod.convert_contact(legacy_row())
    assert out["email"] == "dana.whitfield@example.com"


def test_date_and_sentinel_conversion(mod):
    assert mod.convert_contact(legacy_row())["created_date"] == "2023-06-05"
    assert mod.convert_contact(legacy_row(CREATE_DT="00000000"))["created_date"] is None


def test_convert_all_drops_soft_deleted_and_preserves_order(mod):
    rows = [legacy_row(CONT_ID="K00000001"),
            legacy_row(CONT_ID="K00000002", DEL_FLG="Y"),
            legacy_row(CONT_ID="K00000003")]
    out = mod.convert_all(rows)
    assert [c["contact_id"] for c in out] == ["K00000001", "K00000003"]
    assert all(c is not None for c in out)


def test_convert_all_empty_input_gives_empty_list(mod):
    assert mod.convert_all([]) == []


def test_no_forbidden_imports_in_deliverable(mod):
    src = (case_lib.solution_dir(__file__) / "migrated.py").read_text()
    for banned in ("requests", "urllib", "socket", "subprocess", "http.client"):
        assert banned not in src
# --- Tests added 2026-09-01 after mutation triage (mutant_triage.md #16-#18) ---

def test_verbatim_name_phone_and_owner_fields(mod):
    # first_name/last_name/phone/owner_id are verbatim copies of
    # FRST_NM/LAST_NM/PHONE_TX/OWNER_UID; no prior test asserted their values.
    out = mod.convert_contact(legacy_row())
    assert out["first_name"] == "Dana"
    assert out["last_name"] == "Whitfield"
    assert out["phone"] == "+1-555-0142"
    assert out["owner_id"] == "U0000001"
