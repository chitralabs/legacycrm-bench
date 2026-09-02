"""INT-03 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib

HEADER = "CONT_ID,EMAIL_TX,FRST_NM,LAST_NM,PREF_CH"


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def contact(**over):
    row = {"CONT_ID": "K00000001", "ACCT_ID": "A00000001", "FRST_NM": "Dana",
           "LAST_NM": "Vail", "EMAIL_TX": "dana.vail@example.test",
           "PHONE_TX": "", "PREF_CH": "E", "OPTOUT_FLG": "N",
           "OWNER_UID": "U0000001", "TEAM_CD": "T01",
           "CREATE_DT": "20240110", "DEL_FLG": "N"}
    row.update(over)
    return row


def test_header_row_fixed(mod):
    out = mod.build_payload([contact()])
    assert out.split("\n")[0] == HEADER


def test_basic_contact_row(mod):
    out = mod.build_payload([contact()])
    assert out == HEADER + "\nK00000001,dana.vail@example.test,Dana,Vail,E\n"


def test_opted_out_contact_id_never_in_payload(mod):
    # Privacy negative: the opted-out contact's id appears nowhere.
    opted = contact(CONT_ID="K00000009", EMAIL_TX="optout@example.test",
                    FRST_NM="Opal", LAST_NM="Utter", OPTOUT_FLG="Y")
    out = mod.build_payload([contact(), opted])
    assert "K00000009" not in out


def test_opted_out_contact_email_and_name_never_in_payload(mod):
    opted = contact(CONT_ID="K00000009", EMAIL_TX="optout@example.test",
                    FRST_NM="Opal", LAST_NM="Utter", OPTOUT_FLG="Y")
    out = mod.build_payload([contact(), opted])
    assert "optout@example.test" not in out
    assert "Opal" not in out
    assert "Utter" not in out


def test_soft_deleted_contact_excluded(mod):
    gone = contact(CONT_ID="K00000042", EMAIL_TX="ghost@example.test", DEL_FLG="Y")
    out = mod.build_payload([contact(), gone])
    assert "K00000042" not in out
    assert "ghost@example.test" not in out


def test_soft_deleted_and_opted_out_excluded(mod):
    both = contact(CONT_ID="K00000077", DEL_FLG="Y", OPTOUT_FLG="Y")
    out = mod.build_payload([both])
    assert out == HEADER + "\n"


def test_blank_optout_flag_means_included(mod):
    # Blank CHAR(1) boolean means 'N' (SYSTEM_OVERVIEW.md section 1).
    out = mod.build_payload([contact(OPTOUT_FLG="")])
    assert "K00000001" in out


def test_blank_pref_ch_defaults_to_E(mod):
    out = mod.build_payload([contact(PREF_CH="")])
    assert out.split("\n")[1].endswith(",E")


def test_pref_ch_phone_preserved(mod):
    out = mod.build_payload([contact(PREF_CH="P")])
    assert out.split("\n")[1].endswith(",P")


def test_comma_in_field_is_quoted(mod):
    out = mod.build_payload([contact(LAST_NM="Vail, Jr.")])
    assert out.split("\n")[1] == 'K00000001,dana.vail@example.test,Dana,"Vail, Jr.",E'


def test_quote_in_field_is_doubled_and_quoted(mod):
    out = mod.build_payload([contact(FRST_NM='Dana "Dee"')])
    assert out.split("\n")[1] == 'K00000001,dana.vail@example.test,"Dana ""Dee""",Vail,E'


def test_empty_input_yields_header_only(mod):
    assert mod.build_payload([]) == HEADER + "\n"


def test_input_order_preserved(mod):
    a = contact(CONT_ID="K00000003", EMAIL_TX="c3@example.test")
    b = contact(CONT_ID="K00000001", EMAIL_TX="c1@example.test")
    c = contact(CONT_ID="K00000002", EMAIL_TX="c2@example.test")
    rows = mod.build_payload([a, b, c]).rstrip("\n").split("\n")[1:]
    assert [r.split(",")[0] for r in rows] == ["K00000003", "K00000001", "K00000002"]


def test_payload_ends_with_single_trailing_newline(mod):
    out = mod.build_payload([contact()])
    assert out.endswith("\n") and not out.endswith("\n\n")
