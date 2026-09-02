"""WFL-03 reference solution: order_fulfilment workflow migrated from workflows.xml.

Preserves legacy engine semantics (SYSTEM_OVERVIEW.md §3): first-match-in-document-order
(cancel rows are distinguished by their from-state), VRL LOOKUP against live rows only,
NVL/empty-string numeric coercion, WF_NOMATCH no-op.
"""


def _s(record, field):
    v = record.get(field, "")
    return "" if v is None else str(v)


def _n(record, field):
    v = record.get(field, "")
    if v is None or v == "":
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _lookup(tables, table, key_col, key_val, out_col):
    """VRL LOOKUP: first live row's out_col, else empty string (SYSTEM_OVERVIEW.md §2)."""
    for row in tables.get(table, []):
        if _s(row, "DEL_FLG") == "Y":
            continue
        if _s(row, key_col) == str(key_val):
            return _s(row, out_col)
    return ""


def _g_approve(r, tables):
    return _n(r, "TOT_AMT") > 0  # NVL(TOT_AMT,0) > 0


def _g_cancel_no_hold(r, tables):
    # LOOKUP(ACCT_MASTER, ACCT_ID, ACCT_ID, CRED_HOLD) <> 'Y'
    return _lookup(tables, "ACCT_MASTER", "ACCT_ID", _s(r, "ACCT_ID"), "CRED_HOLD") != "Y"


# (from, event, to, guard, audits, notifies) in document order.
_TRANSITIONS = [
    ("E", "approve", "A", _g_approve, ["ORD_APPR"], []),
    ("A", "ship", "S", None, ["ORD_SHIP"], ["shipped"]),
    ("S", "invoice", "I", None, ["ORD_INV"], []),
    ("E", "cancel", "X", None, ["ORD_CANC"], []),
    ("A", "cancel", "X", _g_cancel_no_hold, ["ORD_CANC"], []),
    ("I", "cancel", "X", None, ["ORD_CANC_INV"], ["credit_note"]),
]


def fire(state, event, record, tables):
    tables = tables or {}
    for frm, ev, to, guard, audits, notifies in _TRANSITIONS:
        if frm == state and ev == event and (guard is None or guard(record, tables)):
            return {"state": to, "record": dict(record), "audits": list(audits),
                    "notifies": list(notifies), "matched": True}
    return {"state": state, "record": dict(record), "audits": ["WF_NOMATCH"],
            "notifies": [], "matched": False}
