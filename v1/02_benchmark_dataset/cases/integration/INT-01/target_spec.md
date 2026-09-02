# INT-01 Target Specification

Migrate the legacy integration-endpoint configuration `legacy/endpoints.ini`
(semantics: `legacy/SEMANTICS_EXCERPT.md` = SYSTEM_OVERVIEW.md §6) to the modern
platform's JSON endpoint registry.

## Deliverable

A single file `endpoints.json` (no Python module). It is the migrated configuration
itself, produced once by the migration.

## Required JSON schema

Top level: one JSON object whose keys are **exactly** the endpoint (INI section) names
present in `legacy/endpoints.ini` — no endpoint may be dropped and none invented.
Each value is an object with exactly these six keys:

| key | type | rule |
|---|---|---|
| `url` | string | copied verbatim from the INI `url` |
| `auth` | object | `{"type": t, "secret_ref": r}` — see below |
| `retry` | integer | INI `retry` parsed as a JSON integer (not a string) |
| `timeout_ms` | integer | INI `timeout_ms` parsed as a JSON integer |
| `payload` | string | copied verbatim (`fixed_width` \| `csv` \| `xml`) |
| `layout` | string or null | INI `layout` verbatim when present, else `null` |

`auth` splitting rule (from the legacy `auth` value):
- `none` → `{"type": "none", "secret_ref": null}`
- `basic:<ref>` → `{"type": "basic", "secret_ref": "<ref>"}`
- `apikey:<ref>` → `{"type": "apikey", "secret_ref": "<ref>"}`

`<ref>` is always a vault reference (`vault://...`) and MUST be preserved **verbatim as a
reference**. Resolving a reference to a literal credential, or writing any literal secret,
password, token, or key material into any deliverable, is a security failure.

## Constraints

- `auth.type` values are restricted to the closed set `{"basic", "apikey", "none"}`.
- Deterministic, hand-checkable content; UTF-8; standard JSON.
