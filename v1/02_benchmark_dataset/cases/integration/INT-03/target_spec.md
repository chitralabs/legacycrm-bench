# INT-03 Target Specification

Rebuild the CSV payload builder for the `marketing_sync` integration
(`legacy/marketing_sync_endpoint.ini`; column semantics `legacy/cont_master_columns.csv`;
conventions `legacy/SEMANTICS_EXCERPT.md`) as **one Python module** `migrated.py`.

## Required interface

```python
def build_payload(contacts: list[dict]) -> str: ...
```

`contacts` is a list of CONT_MASTER rows (dicts of strings; missing keys behave as
empty string).

## Required behavior

1. **Header row (fixed, exactly):** `CONT_ID,EMAIL_TX,FRST_NM,LAST_NM,PREF_CH`
2. One data row per **includable** contact, in **input order**. A contact is includable
   iff BOTH:
   - not soft-deleted: `DEL_FLG` is not `'Y'` (blank means `N`), and
   - not opted out: `OPTOUT_FLG` is not `'Y'` (blank means `N`).

   **Privacy invariant:** no field of an opted-out or soft-deleted contact — not its id,
   not its email, not its name — may appear anywhere in the payload.
3. Field values are taken verbatim from the row, except `PREF_CH`: blank/missing is
   written as `E` (data dictionary: blank=E).
4. **RFC-4180-style quoting:** a field containing a comma, a double quote, a CR or an
   LF is enclosed in double quotes, with embedded double quotes doubled. Other fields
   are unquoted.
5. Rows are separated by `\n` and the payload ends with a trailing `\n` (the header row
   included: an empty contact list yields `"CONT_ID,EMAIL_TX,FRST_NM,LAST_NM,PREF_CH\n"`).

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
