"""WFL-01 reference solution: opportunity_pipeline workflow migrated from workflows.xml.

Preserves legacy engine semantics (SYSTEM_OVERVIEW.md §3): first-match-in-document-order,
guard evaluation with VRL coercions, sets applied after state change in order, WF_NOMATCH
no-op, audit/notify collection in action order.
"""

SENTINEL = "00000000"


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


def _g_qualify(r):
    return _n(r, "AMT") > 0  # NVL(AMT,0) > 0


def _g_close_won(r):
    return _s(r, "CLOSE_DT") != SENTINEL  # CLOSE_DT <> '00000000'


def _g_close_lost(r):
    return _s(r, "LOST_RSN") != ""  # LOST_RSN <> ''


# (from, event, to, guard, actions) in document order; actions are ("set", f, v) /
# ("audit", code) / ("notify", template) in document order.
_TRANSITIONS = [
    ("P", "qualify", "Q", _g_qualify,
     [("set", "STAGE_PCT", "25"), ("audit", "OPP_QUAL")]),
    ("Q", "advance", "N", None,
     [("set", "STAGE_PCT", "60")]),
    ("N", "close_won", "W", _g_close_won,
     [("set", "STAGE_PCT", "100"), ("audit", "OPP_WON"), ("notify", "won_deal")]),
    ("P", "close_lost", "L", _g_close_lost,
     [("set", "STAGE_PCT", "0"), ("audit", "OPP_LOST")]),
    ("Q", "close_lost", "L", _g_close_lost,
     [("set", "STAGE_PCT", "0"), ("audit", "OPP_LOST")]),
    ("N", "close_lost", "L", _g_close_lost,
     [("set", "STAGE_PCT", "0"), ("audit", "OPP_LOST")]),
]


def fire(state, event, record):
    for frm, ev, to, guard, actions in _TRANSITIONS:
        if frm == state and ev == event and (guard is None or guard(record)):
            new = dict(record)
            audits, notifies = [], []
            for action in actions:  # sets apply after state change, in order
                if action[0] == "set":
                    new[action[1]] = action[2]
                elif action[0] == "audit":
                    audits.append(action[1])
                elif action[0] == "notify":
                    notifies.append(action[1])
            return {"state": to, "record": new, "audits": audits,
                    "notifies": notifies, "matched": True}
    return {"state": state, "record": dict(record), "audits": ["WF_NOMATCH"],
            "notifies": [], "matched": False}
