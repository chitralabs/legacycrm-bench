"""SCR-03 reference solution: case_escalation.crms migrated to an event-producing service.

Preserves legacy semantics (SYSTEM_OVERVIEW.md §4 + case_escalation.crms): DATEDIFF as
whole calendar days with the 00000000-sentinel-yields-0 rule, N-cases overdue at >= 2
days, A-cases at >= 7 days only when not already escalated, live rows only, primary-key
ascending order, injected today.
"""
import datetime

SENTINEL = "00000000"


def _s(row, field):
    v = row.get(field, "")
    return "" if v is None else str(v)


def _to_date(yyyymmdd):
    return datetime.date(int(yyyymmdd[0:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8]))


def _datediff(d1, d2):
    """DATEDIFF(d1, d2): whole days d1 - d2; 0 if either is the sentinel (or no value)."""
    if d1 == SENTINEL or d2 == SENTINEL or len(d1) != 8 or len(d2) != 8:
        return 0
    try:
        return (_to_date(d1) - _to_date(d2)).days
    except ValueError:
        return 0


def escalate(cases, today):
    events = []
    live = [c for c in cases if _s(c, "DEL_FLG") != "Y"]
    for c in sorted(live, key=lambda r: _s(r, "CASE_ID")):  # primary key ascending
        age = _datediff(str(today), _s(c, "OPEN_DT"))
        stat = _s(c, "STAT_CD")
        if stat == "N" and age >= 2:
            events.append({"workflow": "case_lifecycle",
                           "entity_id": _s(c, "CASE_ID"),
                           "event": "auto_escalate"})
        elif stat == "A" and _s(c, "ESC_FLG") != "Y" and age >= 7:
            events.append({"workflow": "case_lifecycle",
                           "entity_id": _s(c, "CASE_ID"),
                           "event": "auto_escalate"})
    return events
