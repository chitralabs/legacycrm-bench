# SCH-02 Target Specification

Migrate the legacy `CONT_MASTER` row shape (`legacy/cont_master.sql`, conventions in
`legacy/SEMANTICS_EXCERPT.md` and `legacy/data_dictionary_excerpt.csv`) to the modern
`contact` record shape as **one Python module** `migrated.py`.

## Required interface

```python
def convert_contact(row: dict) -> dict | None: ...
def convert_all(rows: list[dict]) -> list[dict]: ...
```

- `row`: one legacy `CONT_MASTER` row with string values. Missing keys behave as empty string.
- `convert_contact` returns `None` when `DEL_FLG == 'Y'`; otherwise the converted dict.
- `convert_all` converts a list of rows, **dropping soft-deleted rows** and **preserving the
  input order** of the surviving rows. It never returns `None` entries.

## Field mapping (exact; output must contain exactly these 11 keys and no others)

| Legacy column | Modern key          | Conversion |
|---------------|---------------------|------------|
| CONT_ID       | `contact_id`        | string, verbatim |
| ACCT_ID       | `account_id`        | string, verbatim |
| FRST_NM       | `first_name`        | string, verbatim |
| LAST_NM       | `last_name`         | string, verbatim |
| EMAIL_TX      | `email`             | string; blank/missing → `None` |
| PHONE_TX      | `phone`             | string, verbatim |
| PREF_CH       | `preferred_channel` | enum string: `'E'`→`"email"`, `'P'`→`"phone"`, `'M'`→`"mail"`, blank/missing→`"email"` (per data dictionary `blank=E`) |
| OPTOUT_FLG    | `marketing_optout`  | `bool`; `'Y'` → `True`; anything else (`'N'`, blank, missing) → `False` |
| OWNER_UID     | `owner_id`          | string, verbatim |
| TEAM_CD       | `team_code`         | string, verbatim |
| CREATE_DT     | `created_date`      | ISO `YYYY-MM-DD`; sentinel `00000000` (or blank/missing) → `None` |

`DEL_FLG` is not mapped: soft deletion is expressed by `None` (convert_contact) or omission
(convert_all). No legacy column name may appear as a key of the output.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
