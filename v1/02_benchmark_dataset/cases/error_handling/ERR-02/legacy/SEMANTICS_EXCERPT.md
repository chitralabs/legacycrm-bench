# Excerpt of legacy_system/SYSTEM_OVERVIEW.md (authoritative semantics)

## 6. Integrations — semantics

`endpoints.ini`: INI sections per endpoint with `url`, `auth` (`none` | `basic:<secret_ref>` |
`apikey:<secret_ref>`), `retry` (count), `timeout_ms`, `payload` (`fixed_width` | `csv` | `xml`).
Secrets are **references** into a vault (`vault://...`), never literal credentials.

## 7. Batch jobs — semantics (retry-count convention shared by the integration dispatcher)

`RETRY:n` re-runs the failing work up to n times, i.e. the initial attempt plus up to n
re-attempts (at most n + 1 attempts in total).
