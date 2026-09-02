# ERR-01 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from the CRMScript
semantics in `legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §4, §2). No LLM output was
used to produce expectations. Derivations:

1. Ordinary division is untouched by the quirk: 10 / 4 = 2.5, no audit.
2. §4: "Numeric division by zero yields 0 and logs audit `SCRIPT_DIV0`" → 7 / 0 = (0.0,
   ["SCRIPT_DIV0"]), exactly one code.
3. 0 / 0 is still "division by zero" → same quirk result; the value must be the number 0,
   never NaN (checked with the value == value self-comparison).
4. The legacy engine never raises on a zero divisor; the migration must not either — the
   negative expectation is asserted by calling every zero-divisor form inside try/except and
   failing on any exception.
5. §2/§4 numeric coercion: empty string coerces to 0 in numeric context → "" / 5 = 0.0 with
   no audit (the *divisor* is 5, non-zero).
6. Same coercion on the divisor: 5 / "" → divisor coerces to 0 → quirk → (0.0,
   ["SCRIPT_DIV0"]).
7. §4: uninitialized variables read as empty string → None models an uninitialized operand →
   5 / None behaves like 5 / "" → quirk.
8. Numeric strings coerce to their numeric value: "9" / "3" = 3.0, no audit.
9. "0" coerces to numeric 0 → quirk fires.
10. Negative expectation: a successful division emits no audit codes at all.
11. The quirk's value is the number 0 (§4 "yields 0"): not None, not a string; int or float
    accepted, equality with 0 required.
12. Sign handling is plain arithmetic: -9/3 = -3.0 and 9/-3 = -3.0 (a negative divisor is not
    zero, so no quirk).
13. Security/scan expectation: no network/subprocess imports (as in the VAL-01 exemplar).
