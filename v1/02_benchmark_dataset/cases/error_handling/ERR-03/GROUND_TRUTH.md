# ERR-03 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/validation_rules.vrl` and the VRL semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §2). No LLM output was used to produce expectations. Derivations:

1. **The code registry** is read off the rule file by hand: ACC rules E1001–E1005 (5), CON
   rules E2001–E2004 (4), OPP rules E3001–E3007 (7), CAS rules E4001–E4004 (4), ORD rules
   E5001–E5005 (5) — 25 distinct codes. The in-test regex `ERROR\s+(E\d{4})` re-derives the
   same list from the artifact and the sanity assertion pins it at 25.
2. Empty failure list: §2 — a write with no failures proceeds; blocked False, status 200
   (target-spec mapping of "write allowed"), empty errors list.
3. One BLOCK failure (E3001 "Amount negative", severity default BLOCK per §2): blocked True,
   status 422, entry preserved verbatim.
4. WARN-only (E3007 is the OPP WARN rule): §2 — "SEVERITY WARN allows the write" → blocked
   False, status 200, yet the failure is still *reported* (the legacy engine logs it), so the
   errors list retains it with severity WARN.
5. Mixed WARN (E1005, the ACC-005 WARN rule) + BLOCK (E1001): any BLOCK failure blocks the
   write (§2) → blocked True; both entries retained in input order (WARN first here).
6. §2: "**all** BLOCK failures for the write are collected and reported together" → no code
   may be dropped: five distinct codes in, the same five out, same order.
7. Order preservation: §2 fixes collection order as rule-file order, so the reporter must not
   re-sort; a deliberately reverse-sorted input must come back unchanged (negative test
   against alphabetical sorting).
8. Duplicates: the reporter maps entries 1:1 ("one entry per input entry", target-spec rule 3);
   two E3001 entries stay two entries.
9. Every one of the 25 legacy codes round-trips (the registry must not silently drop rare
   tables' codes such as the CAS or ORD families).
10. Hallucination guard: E9999, X123, and an invented E8888 hidden between valid codes are not
    in the rule file → ValueError (target-spec rule 1; there is no rule in the legacy system
    that could ever produce them). Negative security expectations.
11. `type` and `title` are the fixed target-spec strings; document keys are exactly
    {type, title, status, blocked, errors} and error keys exactly {code, message, severity}.
12. Source scan: every `E\d{4}` literal in the delivered module must appear in the legacy rule
    file — a migration that hardcodes extra codes fails even if it never emits them.
