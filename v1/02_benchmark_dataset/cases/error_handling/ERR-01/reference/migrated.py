"""ERR-01 reference solution: legacy CRMScript division-by-zero quirk, preserved.

SYSTEM_OVERVIEW.md §4: numeric division by zero yields 0 and logs audit SCRIPT_DIV0.
Legacy numeric coercion: empty string / None coerce to 0; numeric strings to their value.
"""


def _n(value):
    if value is None or value == "":
        return 0.0
    return float(value)


def safe_div(a, b):
    num = _n(a)
    den = _n(b)
    if den == 0:
        return 0.0, ["SCRIPT_DIV0"]
    return num / den, []
