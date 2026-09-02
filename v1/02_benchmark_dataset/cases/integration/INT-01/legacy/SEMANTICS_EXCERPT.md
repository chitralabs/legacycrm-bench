# Excerpt from SYSTEM_OVERVIEW.md (Meridian CRM 4.2, authoritative semantics)

## 6. Integrations — semantics

`endpoints.ini`: INI sections per endpoint with `url`, `auth` (`none` | `basic:<secret_ref>` |
`apikey:<secret_ref>`), `retry` (count), `timeout_ms`, `payload` (`fixed_width` | `csv` | `xml`).
Secrets are **references** into a vault (`vault://...`), never literal credentials. Fixed-width
payload layouts are in `data_dictionary.csv` rows with DICT_TYPE=LAYOUT.
