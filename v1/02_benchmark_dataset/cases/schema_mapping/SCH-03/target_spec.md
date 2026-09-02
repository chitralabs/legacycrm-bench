# SCH-03 Target Specification

Migrate the legacy `OPP_MASTER` row shape (`legacy/opp_master.sql`, code meanings in
`legacy/data_dictionary_excerpt.csv`, conventions in `legacy/SEMANTICS_EXCERPT.md`) to the
modern `opportunity` record shape as **one Python module** `migrated.py`.

## Required interface

```python
def convert_opportunity(row: dict) -> dict | None: ...
```

- `row`: one legacy `OPP_MASTER` row with string values. Missing keys behave as empty string.
- Returns `None` when `DEL_FLG == 'Y'`; otherwise the converted dict.

## Stage collapse (STAT_CD + STAGE_PCT → one `stage` enum)

`STAGE_PCT` is a redundant legacy duplicate of `STAT_CD`. The modern record keeps **one**
`stage` field, always derived from `STAT_CD` (STAT_CD is the trusted source):

| STAT_CD | `stage`         | canonical STAGE_PCT |
|---------|-----------------|---------------------|
| P       | `"prospecting"` | 10  |
| Q       | `"qualified"`   | 25  |
| N       | `"negotiation"` | 60  |
| W       | `"closed_won"`  | 100 |
| L       | `"closed_lost"` | 0   |

When the row's `STAGE_PCT` (numeric; blank/missing coerces to 0 per the legacy convention)
differs from the canonical value for its `STAT_CD`, the record is still mapped from `STAT_CD`
but `migration_flags` must contain `"stage_pct_mismatch"`. `migration_flags` is always
present as a list; it is `[]` when nothing is flagged. (Consequence: `STAT_CD='L'` with blank
`STAGE_PCT` is NOT a mismatch, because blank coerces to 0 = canonical for L.)

## Amount → integer minor units

`amount_minor` is `AMT` converted to an **int** of currency minor units:
`amount_minor = round_half_up(AMT × 10^exponent)`. The currency exponent is **0 for JPY**
(yen has no decimal subdivision) and **2 for every other currency appearing in this dataset**.
Half-up rounding is the documented legacy convention (ZPAD, §4 excerpt). Blank/missing `AMT`
coerces to 0. `currency` is `CURR_CD`, blank/missing → `"USD"` (and then exponent 2).

## Field mapping (exact; output must contain exactly these 13 keys and no others)

| Legacy column | Modern key        | Conversion |
|---------------|-------------------|------------|
| OPP_ID        | `opportunity_id`  | string, verbatim |
| ACCT_ID       | `account_id`      | string, verbatim |
| OPP_NM        | `name`            | string, verbatim |
| STAT_CD + STAGE_PCT | `stage`     | enum per table above (from STAT_CD only) |
| AMT + CURR_CD | `amount_minor`    | int minor units per rule above |
| CURR_CD       | `currency`        | string; blank/missing → `"USD"` |
| CLOSE_DT      | `close_date`      | ISO `YYYY-MM-DD`; sentinel `00000000` (or blank/missing) → `None` |
| OWNER_UID     | `owner_id`        | string, verbatim |
| TEAM_CD       | `team_code`       | string, verbatim |
| LOST_RSN      | `lost_reason`     | string code verbatim; blank/missing → `None` |
| CREATE_DT     | `created_date`    | ISO or `None` (sentinel) |
| UPD_DT        | `updated_date`    | ISO or `None` (sentinel) |
| (derived)     | `migration_flags` | list per rule above |

`DEL_FLG` and `STAGE_PCT` are not mapped as keys. No legacy column name may appear as a key
of the output.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
