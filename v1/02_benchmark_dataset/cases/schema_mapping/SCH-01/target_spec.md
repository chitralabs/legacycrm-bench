# SCH-01 Target Specification

Migrate the legacy `ACCT_MASTER` row shape (`legacy/acct_master.sql`, conventions in
`legacy/SEMANTICS_EXCERPT.md` and `legacy/data_dictionary_excerpt.csv`) to the modern
`account` record shape as **one Python module** `migrated.py`.

## Required interface

```python
def convert_account(row: dict) -> dict | None: ...
```

- `row`: one legacy `ACCT_MASTER` row with **string values** for every column (as read from a
  legacy CSV extract). Missing keys behave as empty string.
- Returns `None` when the row is soft-deleted (`DEL_FLG == 'Y'`); otherwise the converted dict.

## Field mapping (exact; output must contain exactly these 13 keys and no others)

| Legacy column | Modern key       | Conversion |
|---------------|------------------|------------|
| ACCT_ID       | `account_id`     | string, verbatim |
| ACCT_NM       | `name`           | string, verbatim |
| ACCT_TYP      | `account_type`   | string, code verbatim |
| SIC_CD        | `sic_code`       | string, verbatim |
| REGION_CD     | `region`         | string, verbatim |
| ANN_REV       | `annual_revenue` | `float`; blank/missing → `0.0` (legacy empty-numeric-is-zero convention) |
| CURR_CD       | `currency`       | string; blank/missing → `"USD"` |
| OWNER_UID     | `owner_id`       | string, verbatim |
| TEAM_CD       | `team_code`      | string, verbatim |
| CRED_LIMIT    | `credit_limit`   | `float`; blank/missing → `0.0` |
| CRED_HOLD     | `credit_hold`    | `bool`; `'Y'` → `True`; `'N'`/blank/missing → `False` |
| CREATE_DT     | `created_date`   | ISO `YYYY-MM-DD` string; sentinel `00000000` (or blank/missing) → `None` |
| UPD_DT        | `updated_date`   | same as `created_date` |

`DEL_FLG` is not mapped: soft deletion is expressed by the `None` return value. No legacy
column name may appear as a key of the output.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
