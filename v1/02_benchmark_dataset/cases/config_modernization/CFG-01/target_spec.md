# CFG-01 Target Specification

Extract the legacy code tables from the COLUMN rows of `legacy/data_dictionary.csv`
(conventions: `legacy/SEMANTICS_EXCERPT.md`) into one modern configuration file
**`enums.json`** — the single deliverable.

## Required shape

Top-level JSON object with **exactly** these eight keys (one per enumerated code table),
each mapping legacy code → modern label:

```json
{
  "ACCT_MASTER.ACCT_TYP": {"<code>": "<label>", ...},
  "CONT_MASTER.PREF_CH": {...},
  "OPP_MASTER.STAT_CD": {...},
  "OPP_MASTER.LOST_RSN": {...},
  "CASE_MASTER.SEV_CD": {...},
  "CASE_MASTER.STAT_CD": {...},
  "ORD_HEADER.STAT_CD": {...},
  "ACT_LOG.ACT_TYP": {...}
}
```

## Extraction rules

1. Source of truth: the `MEANING` field of DICT_TYPE=COLUMN rows, parsed as
   semicolon-separated `code=label` pairs. Labels must be reproduced with **exact fidelity**
   (`"Closed-Won"`, `"Pending-Customer"`, `"no budget"` — punctuation, case, and internal
   spaces preserved).
2. Strip parenthesized operational annotations from labels: `Prospecting(10%)` →
   `Prospecting`; `Critical(4h target)` → `Critical`. The annotation is not part of the label.
3. Default notes are **not** codes: `blank=E` (PREF_CH) is a storage default — no blank/empty
   key may appear in any map.
4. Only enumerated code tables are enums. Convention rows are excluded: `CURR_CD`
   (ISO-4217 reference, not an enum), `CRED_HOLD` and `OPTOUT_FLG` (Y/N booleans),
   `ALL.DEL_FLG`, and `ALL.*_DT` must NOT appear as keys.
5. No invented codes and no invented tables: every code in `enums.json` must exist in the
   dictionary MEANING for that column, and every documented code must be present.

## Deliverable

- `enums.json` only (valid JSON, UTF-8).
