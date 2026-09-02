"""INT-03 reference solution: marketing_sync CSV payload builder.

Excludes opted-out (OPTOUT_FLG='Y') and soft-deleted (DEL_FLG='Y') contacts entirely
(privacy invariant), defaults blank PREF_CH to 'E', quotes RFC-4180 style, and joins
rows with a trailing newline. Blank flags mean 'N' (SYSTEM_OVERVIEW.md §1).
"""

HEADER = ["CONT_ID", "EMAIL_TX", "FRST_NM", "LAST_NM", "PREF_CH"]


def _s(row, field):
    v = row.get(field, "")
    return "" if v is None else str(v)


def _flag(row, field):
    return _s(row, field) == "Y"


def _quote(field):
    if any(ch in field for ch in (',', '"', '\r', '\n')):
        return '"' + field.replace('"', '""') + '"'
    return field


def _row_values(c):
    pref = _s(c, "PREF_CH") or "E"
    return [_s(c, "CONT_ID"), _s(c, "EMAIL_TX"), _s(c, "FRST_NM"),
            _s(c, "LAST_NM"), pref]


def build_payload(contacts):
    lines = [",".join(HEADER)]
    for c in contacts:
        if _flag(c, "DEL_FLG") or _flag(c, "OPTOUT_FLG"):
            continue  # privacy: excluded contacts contribute nothing at all
        lines.append(",".join(_quote(v) for v in _row_values(c)))
    return "\n".join(lines) + "\n"
