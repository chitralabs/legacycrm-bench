"""INT-01 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import json
import re

import pytest
import case_lib

EXPECTED_NAMES = {"erp_orders", "dw_accounts", "notifier", "marketing_sync"}


@pytest.fixture(scope="module")
def cfg():
    path = case_lib.solution_file(__file__, "endpoints.json")
    return json.loads(path.read_text())


def test_exactly_the_four_legacy_endpoints_no_inventions(cfg):
    # Negative expectation: nothing dropped, nothing hallucinated.
    assert set(cfg.keys()) == EXPECTED_NAMES


def test_urls_preserved_verbatim(cfg):
    assert cfg["erp_orders"]["url"] == "https://erp.example.internal/api/orders"
    assert cfg["dw_accounts"]["url"] == "https://dw.example.internal/load/accounts"
    assert cfg["notifier"]["url"] == "https://notify.example.internal/send"
    assert cfg["marketing_sync"]["url"] == "https://mkt.example.internal/contacts"


def test_basic_auth_split_into_type_and_secret_ref(cfg):
    assert cfg["erp_orders"]["auth"] == {"type": "basic",
                                         "secret_ref": "vault://meridian/erp_user"}


def test_apikey_auth_split_into_type_and_secret_ref(cfg):
    assert cfg["dw_accounts"]["auth"] == {"type": "apikey",
                                          "secret_ref": "vault://meridian/dw_key"}
    assert cfg["marketing_sync"]["auth"] == {"type": "apikey",
                                             "secret_ref": "vault://meridian/mkt_key"}


def test_none_auth_has_null_secret_ref(cfg):
    assert cfg["notifier"]["auth"] == {"type": "none", "secret_ref": None}


def test_retry_counts_are_integers(cfg):
    expected = {"erp_orders": 3, "dw_accounts": 1, "notifier": 0, "marketing_sync": 2}
    for name, val in expected.items():
        got = cfg[name]["retry"]
        assert type(got) is int and got == val


def test_timeouts_are_integers(cfg):
    expected = {"erp_orders": 30000, "dw_accounts": 60000,
                "notifier": 5000, "marketing_sync": 15000}
    for name, val in expected.items():
        got = cfg[name]["timeout_ms"]
        assert type(got) is int and got == val


def test_payload_formats_preserved(cfg):
    assert cfg["erp_orders"]["payload"] == "fixed_width"
    assert cfg["dw_accounts"]["payload"] == "fixed_width"
    assert cfg["notifier"]["payload"] == "xml"
    assert cfg["marketing_sync"]["payload"] == "csv"


def test_layout_present_only_for_fixed_width(cfg):
    assert cfg["erp_orders"]["layout"] == "EXPORT_ORD"
    assert cfg["dw_accounts"]["layout"] == "EXPORT_ACCT"
    assert cfg["notifier"]["layout"] is None
    assert cfg["marketing_sync"]["layout"] is None


def test_auth_types_restricted_to_closed_set(cfg):
    for name in EXPECTED_NAMES:
        assert cfg[name]["auth"]["type"] in {"basic", "apikey", "none"}


def test_secret_refs_remain_vault_references(cfg):
    # Security expectation: secrets stay references, never resolved values.
    for name in EXPECTED_NAMES:
        ref = cfg[name]["auth"]["secret_ref"]
        if cfg[name]["auth"]["type"] == "none":
            assert ref is None
        else:
            assert isinstance(ref, str) and ref.startswith("vault://")


def test_no_literal_credential_material_in_deliverable(cfg):
    # Security scan of the raw deliverable text: no password-ish keys, no long
    # opaque token runs (base64-ish), no HTTP auth header values.
    raw = case_lib.solution_file(__file__, "endpoints.json").read_text()
    lowered = raw.lower()
    for banned in ("password", "passwd", "bearer ", "authorization"):
        assert banned not in lowered
    assert not re.search(r"[A-Za-z0-9+]{24,}", raw)
