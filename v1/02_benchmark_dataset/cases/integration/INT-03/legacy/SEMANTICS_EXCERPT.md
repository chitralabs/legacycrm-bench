# Excerpts from SYSTEM_OVERVIEW.md (Meridian CRM 4.2, authoritative semantics)

## 1. Entities and storage (conventions, excerpt)

Legacy conventions that migrations must handle:
- **Sentinel values.** Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`.
- **Soft delete.** `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them
  unless stated.

CONT_MASTER column semantics (data_dictionary.csv, this case: `cont_master_columns.csv`):
- `PREF_CH`: E=email; P=phone; M=mail; blank=E.
- `OPTOUT_FLG`: Y = excluded from **all** marketing communications.

## 6. Integrations — semantics (excerpt)

`endpoints.ini`: INI sections per endpoint with `url`, `auth`, `retry`, `timeout_ms`,
`payload` (`fixed_width` | `csv` | `xml`). The `marketing_sync` endpoint
(this case: `marketing_sync_endpoint.ini`) receives a `csv` payload of marketable contacts.
