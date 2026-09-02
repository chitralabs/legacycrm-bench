"""RIN-01 reference solution: contact-orphan detection.

Mirrors the first loop of integrity_check.crms: iterate live contacts in CONT_ID
(primary key) order; a contact is an orphan iff LOOKUP against ACCT_MASTER finds no
live account with that ACCT_ID (LOOKUP is blind to soft-deleted rows).
"""


def _s(row, field):
    v = row.get(field, "")
    return "" if v is None else str(v)


def _is_live(row):
    return _s(row, "DEL_FLG") != "Y"  # blank means 'N' (SYSTEM_OVERVIEW.md §1)


def find_orphans(contacts, accounts):
    live_account_ids = {_s(a, "ACCT_ID") for a in accounts if _is_live(a)}
    live_account_ids.discard("")
    live_contacts = sorted(
        (c for c in contacts if _is_live(c)), key=lambda c: _s(c, "CONT_ID")
    )
    return [
        _s(c, "CONT_ID")
        for c in live_contacts
        if _s(c, "ACCT_ID") not in live_account_ids
    ]
