"""WFL-02 reference solution: case_lifecycle workflow migrated from workflows.xml.

Preserves legacy engine semantics (SYSTEM_OVERVIEW.md §3): first-match-in-document-order,
guards with VRL coercions, set actions (literal and =NVL(...) expression) applied after the
state change in order, WF_NOMATCH no-op, audit/notify collection in action order.
Timers are out of scope (posted events only).
"""

SENTINEL = "00000000"


def _s(record, field):
    v = record.get(field, "")
    return "" if v is None else str(v)


def _g_assign(r):
    return _s(r, "OWNER_UID") != ""  # OWNER_UID <> ''


def _g_not_escalated(r):
    return _s(r, "ESC_FLG") != "Y"  # ESC_FLG <> 'Y'


def _g_resolved(r):
    return _s(r, "RES_DT") != SENTINEL  # RES_DT <> '00000000'


def _set_sev_nvl3(rec):
    # value="=NVL(SEV_CD,'3')" evaluated against the evolving record
    return _s(rec, "SEV_CD") if _s(rec, "SEV_CD") != "" else "3"


# (from, event, to, guard, actions) in document order. Actions: ("set", field, literal),
# ("setexpr", field, fn(record)), ("audit", code), ("notify", template).
_TRANSITIONS = [
    ("N", "assign", "A", _g_assign, [("audit", "CASE_ASSIGN")]),
    ("N", "auto_escalate", "A", None,
     [("set", "ESC_FLG", "Y"), ("setexpr", "SEV_CD", _set_sev_nvl3),
      ("audit", "CASE_ESC"), ("notify", "escalation")]),
    ("A", "auto_escalate", "A", _g_not_escalated,
     [("set", "ESC_FLG", "Y"), ("audit", "CASE_ESC"), ("notify", "escalation")]),
    ("A", "await_customer", "P", None, [("audit", "CASE_PEND")]),
    ("P", "customer_reply", "A", None, []),
    ("A", "resolve", "R", _g_resolved, [("audit", "CASE_RES")]),
    ("R", "close", "X", None, [("audit", "CASE_CLOSE")]),
    ("R", "reopen", "A", None,
     [("set", "RES_DT", "00000000"), ("audit", "CASE_REOPEN")]),
]


def fire(state, event, record):
    for frm, ev, to, guard, actions in _TRANSITIONS:
        if frm == state and ev == event and (guard is None or guard(record)):
            new = dict(record)
            audits, notifies = [], []
            for action in actions:  # sets apply after state change, in order
                if action[0] == "set":
                    new[action[1]] = action[2]
                elif action[0] == "setexpr":
                    new[action[1]] = action[2](new)
                elif action[0] == "audit":
                    audits.append(action[1])
                elif action[0] == "notify":
                    notifies.append(action[1])
            return {"state": to, "record": new, "audits": audits,
                    "notifies": notifies, "matched": True}
    return {"state": state, "record": dict(record), "audits": ["WF_NOMATCH"],
            "notifies": [], "matched": False}
