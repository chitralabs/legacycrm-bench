# AUD-01 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/audit_config.cfg` under the audit semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §8). No LLM output was used to produce expectations. Derivations:

1. Reading `audit_config.cfg` line by line: after the one `#` comment header, the 12 `AUDIT`
   lines name exactly five tables — ACCT_MASTER, OPP_MASTER, CASE_MASTER, ORD_HEADER,
   USR_MASTER. Those are the only keys of the parsed dict.
2. ACCT_MASTER lines are `CRED_HOLD`, `CRED_LIMIT`, `OWNER_UID` (cfg lines 2–4) → that exact
   three-element set.
3. OPP_MASTER lines are `STAT_CD`, `AMT`, `OWNER_UID` (lines 5–7).
4. CASE_MASTER lines are `STAT_CD`, `SEV_CD` (lines 8–9); ORD_HEADER lines are `STAT_CD`,
   `DISC_PCT` (lines 10–11).
5. USR_MASTER lines are `ROLE_ID`, `ACTIVE_FLG` (lines 12–13).
6. Negative (no invented columns): `ACCT_MASTER UPD_DT` and `OPP_MASTER OPP_NM` appear nowhere
   in the cfg, so §8 ("audit_config.cfg lists them") makes them non-audited.
7. Negative (no invented tables): CONT_MASTER and ORD_LINE have no AUDIT line, so they must be
   absent from the dict entirely (target spec: unlisted tables absent, not empty).
8. Return type is `dict[str, set[str]]` per the target interface; checked with isinstance.
9. Comment/blank handling comes from the artifact's own format (its first line is a `#`
   comment): hand-crafted text with a comment, a commented-out AUDIT line, and blank lines
   must yield only the two real declarations.
10. Set semantics make duplicate declarations idempotent (target spec rule 3): three identical
    lines yield a one-element set.
11. A file of only comments/blank lines declares nothing → `{}`.
12. Security/scan expectation: deliverable must not import network/subprocess modules
    (same check as the VAL-01 exemplar).
