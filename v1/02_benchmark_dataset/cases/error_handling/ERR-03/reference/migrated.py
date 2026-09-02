"""ERR-03 reference solution: legacy VRL failures -> RFC-7807-style problem document.

Preserves SYSTEM_OVERVIEW.md §2 semantics: every collected failure is retained in collection
order with its legacy code and severity; blocked iff any BLOCK failure; only the error codes
present in validation_rules.vrl exist (hallucination guard raises ValueError on others).
"""

# Exactly the ERROR codes of validation_rules.vrl, in rule-file order.
LEGACY_CODES = frozenset({
    "E1001", "E1002", "E1003", "E1004", "E1005",
    "E2001", "E2002", "E2003", "E2004",
    "E3001", "E3002", "E3003", "E3004", "E3005", "E3006", "E3007",
    "E4001", "E4002", "E4003", "E4004",
    "E5001", "E5002", "E5003", "E5004", "E5005",
})

TYPE_URI = "https://meridian-crm.example/problems/validation"
TITLE = "Legacy validation failed"


def problem_details(errors):
    out_errors = []
    blocked = False
    for e in errors:
        code = e["code"]
        if code not in LEGACY_CODES:
            raise ValueError(f"unknown legacy error code: {code}")
        severity = e["severity"]
        if severity == "BLOCK":
            blocked = True
        out_errors.append({"code": code, "message": e["message"], "severity": severity})
    return {
        "type": TYPE_URI,
        "title": TITLE,
        "status": 422 if blocked else 200,
        "blocked": blocked,
        "errors": out_errors,
    }
