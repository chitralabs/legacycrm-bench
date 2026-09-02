"""RIN-01 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import pytest
import case_lib


@pytest.fixture(scope="module")
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


def acct(acct_id, del_flg="N"):
    return {"ACCT_ID": acct_id, "ACCT_NM": "Account " + acct_id, "DEL_FLG": del_flg}


def cont(cont_id, acct_id, del_flg="N"):
    return {"CONT_ID": cont_id, "ACCT_ID": acct_id, "LAST_NM": "Name", "DEL_FLG": del_flg}


def test_contact_with_live_account_is_not_orphan(mod):
    assert mod.find_orphans([cont("K00000001", "A00000001")],
                            [acct("A00000001")]) == []


def test_contact_with_missing_account_is_orphan(mod):
    assert mod.find_orphans([cont("K00000001", "A00000099")],
                            [acct("A00000001")]) == ["K00000001"]


def test_contact_with_soft_deleted_account_is_orphan(mod):
    # LOOKUP sees live rows only: DEL_FLG='Y' account is invisible.
    assert mod.find_orphans([cont("K00000001", "A00000001")],
                            [acct("A00000001", del_flg="Y")]) == ["K00000001"]


def test_soft_deleted_contact_never_reported(mod):
    # Negative: a dangling but soft-deleted contact is skipped entirely.
    assert mod.find_orphans([cont("K00000001", "A00000099", del_flg="Y")],
                            [acct("A00000001")]) == []


def test_blank_del_flg_account_counts_as_live(mod):
    a = acct("A00000001")
    a["DEL_FLG"] = ""
    assert mod.find_orphans([cont("K00000001", "A00000001")], [a]) == []


def test_blank_acct_id_contact_is_orphan(mod):
    assert mod.find_orphans([cont("K00000001", "")],
                            [acct("A00000001")]) == ["K00000001"]


def test_orphans_ordered_by_cont_id_ascending(mod):
    contacts = [cont("K00000005", "A00000099"),
                cont("K00000002", "A00000099"),
                cont("K00000009", "A00000099")]
    assert mod.find_orphans(contacts, []) == ["K00000002", "K00000005", "K00000009"]


def test_mixed_population(mod):
    accounts = [acct("A00000001"), acct("A00000002", del_flg="Y"), acct("A00000003")]
    contacts = [cont("K00000004", "A00000003"),          # live ref -> ok
                cont("K00000001", "A00000002"),          # soft-deleted acct -> orphan
                cont("K00000003", "A00000404"),          # missing acct -> orphan
                cont("K00000002", "A00000001"),          # live ref -> ok
                cont("K00000005", "A00000404", "Y")]     # deleted contact -> skipped
    assert mod.find_orphans(contacts, accounts) == ["K00000001", "K00000003"]


def test_empty_contacts_yield_empty_list(mod):
    assert mod.find_orphans([], [acct("A00000001")]) == []


def test_no_accounts_means_all_live_contacts_are_orphans(mod):
    contacts = [cont("K00000002", "A00000001"), cont("K00000001", "A00000002")]
    assert mod.find_orphans(contacts, []) == ["K00000001", "K00000002"]


def test_inputs_not_mutated(mod):
    contacts = [cont("K00000001", "A00000099")]
    accounts = [acct("A00000001", del_flg="Y")]
    snap_c = [dict(r) for r in contacts]
    snap_a = [dict(r) for r in accounts]
    mod.find_orphans(contacts, accounts)
    assert contacts == snap_c and accounts == snap_a
