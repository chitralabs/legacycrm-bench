# INT-01 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/endpoints.ini` under the integration semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §6). No LLM output was used to produce expectations. Derivations:

1. Endpoint set: `endpoints.ini` contains exactly four sections — `[erp_orders]`,
   `[dw_accounts]`, `[notifier]`, `[marketing_sync]` — so the JSON object has exactly
   those four keys (test: no inventions, none dropped).
2. URLs are copied verbatim from each section's `url =` line (four literal values in the
   URL test are transcribed character-for-character from the INI).
3. Auth splitting: §6 fixes the legacy grammar `none | basic:<secret_ref> | apikey:<secret_ref>`.
   `erp_orders` has `auth = basic:vault://meridian/erp_user`, so splitting at the first
   colon of the scheme prefix gives type `basic`, secret_ref `vault://meridian/erp_user`.
4. Same rule for `dw_accounts` (`apikey` + `vault://meridian/dw_key`) and
   `marketing_sync` (`apikey` + `vault://meridian/mkt_key`).
5. `notifier` has `auth = none`; there is no secret reference, so the schema in
   target_spec.md maps it to `{"type": "none", "secret_ref": null}`.
6. Retry counts: INI lines `retry = 3 / 1 / 0 / 2` for erp_orders / dw_accounts /
   notifier / marketing_sync; §6 calls retry a count, so the modern value is the JSON
   integer (the test asserts `type(...) is int`, rejecting strings and booleans).
7. Timeouts: INI `timeout_ms = 30000 / 60000 / 5000 / 15000` respectively, as integers
   by the same reasoning.
8. Payload formats verbatim from the INI: fixed_width / fixed_width / xml / csv.
9. Layout: only the two fixed_width endpoints carry a `layout` line
   (`EXPORT_ORD`, `EXPORT_ACCT`); the schema maps an absent layout to `null`, so
   notifier and marketing_sync have `layout: null`.
10. Security expectations follow §6's sentence "Secrets are **references** into a vault
    (`vault://...`), never literal credentials": every non-none secret_ref must start
    with `vault://` and equal the INI value verbatim; the raw-text scan for
    password-like words, HTTP auth header values, and 24+ character opaque token runs
    encodes "no literal credentials appear in the deliverable" (the legal content —
    hostnames, vault paths, format names — contains no alphanumeric run that long,
    verified by hand: longest is "internal", 8 chars).
11. Closed auth-type set {basic, apikey, none} is the full grammar §6 allows; any other
    type is an invention (negative expectation).
