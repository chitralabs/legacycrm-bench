# Surviving-Mutant Triage (LegacyCRM-Bench mutation analysis)

Manual triage of the 28 mutants that survived the AST mutation run
(`03_source_code/harness/mutation_check.py`; survivors listed in
`06_figures_tables/surviving_mutants.csv`; 335/363 killed overall).

Method: for each survivor, the exact mutation was reproduced by importing
`apply_mutation` from the harness, applying it at the recorded `node_index`
(index into `ast.walk` order of the reference file), and diffing
`ast.unparse` output against the original. Every classification below was
additionally **verified empirically**: the mutated module was executed and
compared against the original on the claimed distinguishing input (for
TEST_GAP) or fuzzed/enumerated over the relevant input space (for
EQUIVALENT). No test, reference, or harness file was modified.

Classification key:

- **EQUIVALENT** — provably no observable behavior change for any input in the tested domain.
- **TEST_GAP** — observable behavior changes; no acceptance test distinguishes it.
- **HARNESS_ARTIFACT** — change is outside the behavior the case's spec puts under test.

## Summary table

| # | case_id | file | mutation (one-line diff) | classification | justification |
|---|---------|------|--------------------------|----------------|---------------|
| 1 | AUD-01 | migrated.py (node 52) | `line.startswith('#')` → `line.startswith('#_X')` | EQUIVALENT | The comment check is redundant: a line starting with `#` keeps the `#` in its first whitespace token, so `parts[0] == 'AUDIT'` can never hold and the line is discarded by the format filter anyway. Verified on comment-bearing inputs incl. `"#AUDIT T1 C1"`. |
| 2 | BAT-01 | migrated.py (node 87) | `line.startswith('#')` → `line.startswith('#_X')` | EQUIVALENT | Same redundancy: any `#`-prefixed line has `toks[0]` beginning with `#`, which can never satisfy `toks[0].upper() == 'JOB'`, so the line is skipped by the format filter regardless. Verified. |
| 3 | BIZ-01 | migrated.py (node 142) | `super().__init__(f'{code}: {message}')` → `f'{code}: _X{message}'` | HARNESS_ARTIFACT | Only `str(exc)`/`exc.args` changes; `.code` and `.message` are set separately and unchanged. The spec (`target_spec.md`) requires only the `code` and `message` attributes with exact values, not a `str()` format, so not asserting `str(exc)` is acceptable. |
| 4 | BIZ-02 | migrated.py (node 175) | `super().__init__(f'{code}: {message}')` → `f'{code}: _X{message}'` | HARNESS_ARTIFACT | Identical exception class and reasoning as BIZ-01; BIZ-02's spec likewise requires only the `code`/`message` attributes. Acceptable. |
| 5 | CFG-02 | migrated.py (node 90) | `curr = currency or 'USD'` → `curr = currency or 'USD_X'` | EQUIVALENT | `curr` is consumed only by `exponent = 0 if curr == 'JPY' else 2` and is not returned; `'USD'` and `'USD_X'` are both non-JPY, so the exponent (and output) is identical for every input. Verified incl. blank/None currency. |
| 6 | ERR-02 | migrated.py (node 109) | transient-exhaustion return: key `'result'` → `'result_X'` | TEST_GAP | Spec requires the exact four-key shape with `result: None` on every failure path, but `test_result_shape_keys_exact`/`test_failure_result_is_none` only exercise the success and permanent paths. Exposing input: `call_with_retry({"url":"u","retry":1,"timeout_ms":5}, transport_raising_TransientError_twice)` — mutant returns key `result_X`. |
| 7 | INT-02 | migrated.py (node 13) | `SENTINEL_DATE = '00000000'` → `'00000000_X'` | TEST_GAP | Used as `create_dt = _s(row,'CREATE_DT') or SENTINEL_DATE`; a blank `CREATE_DT` now yields a 79-char record ending `'00000000_X'`. `test_missing_create_dt_written_as_sentinel` only slices `[69:77]` (still `'00000000'`) and the 77-length test uses a non-blank date. Exposing input: `len(format_account(acct(CREATE_DT=""))) == 77`. |
| 8 | INT-02 | migrated.py (node 62) | `_zpad_cents`: default `value = '0'` → `'0_X'` | EQUIVALENT | The default applies only when value is None/`''`; `Decimal('0_X')` raises `InvalidOperation`, which the function's own `except` maps to `Decimal(0)` — exactly the value the original computes — so output is `'0'.rjust(w,'0')` either way. Verified. |
| 9 | SCR-01 | migrated.py (node 242) | `line.get('DEL_FLG', 'N')` → `line.get('DEL_FLG', 'N_X')` | EQUIVALENT | The default is consumed solely by the `== 'Y'` comparison on line 35; any non-`'Y'` default (both `'N'` and `'N_X'`) makes the comparison false identically. Verified on lines with missing/blank/`Y` DEL_FLG. |
| 10 | SCR-03 | migrated.py (node 11) | `SENTINEL = '00000000'` → `'00000000_X'` | EQUIVALENT | `_datediff`'s sentinel short-circuit is redundant: `'00000000'` still passes the `len == 8` check but `_to_date` computes `datetime.date(0, 0, 0)`, which always raises `ValueError` (year/month/day out of range), caught to return 0 — the same result. Verified for sentinel `OPEN_DT`, sentinel `today`, and normal dates. |
| 11 | RBC-01 | migrated.py (node 80) | ADMIN override: `scope = 'ALL'` → `scope = 'ALL_X'` | TEST_GAP | `'ALL_X'` falls into the unknown-scope `else` → deny, so ADMIN is denied everything; RBC-01's tests use REP/MGR/SUPP/GUEST/TEMP but never an ADMIN user, although the legacy matrix has 22 ADMIN rows. Exposing input: `can({"USR_ID":"U0000001","ROLE_ID":"ADMIN","TEAM_CD":"T01"}, "READ", "ACCT_MASTER", foreign_record, rows) is True` (mutant: False). |
| 12 | RBC-01 | migrated.py (node 135) | `del_flg = _s(record,'DEL_FLG') or 'N'` → `or 'N_X'` | TEST_GAP | A blank/missing `DEL_FLG` on DELETE now coerces to `'N_X' != 'N'` → deny, violating the documented blank-means-N rule (§1). Every test record sets `DEL_FLG="N"` explicitly. Exposing input: `can(MGR, "DELETE", "OPP_MASTER", {"OWNER_UID":"U0000003","TEAM_CD":"T01","DEL_FLG":""}, rows) is True` (mutant: False). |
| 13 | RBC-02 | migrated.py (node 186) | `elif scope == 'OWN':` → `elif scope == 'OWN_X':` | TEST_GAP | OWN-scope grants now fall through to the unknown-scope deny. RBC-02's tests focus on ADMIN/DELETE semantics and never exercise a granting OWN row. Exposing input: `can({"USR_ID":"U0000003","ROLE_ID":"REP","TEAM_CD":"T01"}, "UPDATE", "OPP_MASTER", {"OWNER_UID":"U0000003","TEAM_CD":"T01","DEL_FLG":"N"}, rows) is True` (mutant: False). |
| 14 | RBC-03 | migrated.py (node 169) | `policy.get('delete_requires_live_record', True)` → `..., False)` | EQUIVALENT | Only the fallback default changes, and the shipped `policy.json` (a fixed deliverable of the same reference solution, per spec) always contains `"delete_requires_live_record": true`, so the default is dead code in the tested configuration. Verified: 0 decision differences over an 81-tuple enumeration incl. soft-deleted records. |
| 15 | SCH-01 | migrated.py (node 172) | `'owner_id': _s(row,'OWNER_UID')` → `_s(row,'OWNER_UID_X')` | TEST_GAP | `owner_id` becomes `''` for every row; `test_verbatim_string_fields` asserts several fields but not `owner_id` (nor `sic_code`/`credit_limit` values on that path). Exposing input: `convert_account(legacy_row())["owner_id"] == "U0000001"` (mutant: `""`). |
| 16 | SCH-02 | migrated.py (node 163) | `'first_name': _s(row,'FRST_NM')` → `_s(row,'FRST_NM_X')` | TEST_GAP | `first_name` becomes `''` for every contact; no test asserts any name value. Exposing input: `convert_contact(legacy_row())["first_name"] == "Dana"` (mutant: `""`). |
| 17 | SCH-02 | migrated.py (node 172) | `'phone': _s(row,'PHONE_TX')` → `_s(row,'PHONE_TX_X')` | TEST_GAP | `phone` becomes `''`; no test asserts the phone value. Exposing input: `convert_contact(legacy_row())["phone"] == "+1-555-0142"` (mutant: `""`). |
| 18 | SCH-02 | migrated.py (node 181) | `'owner_id': _s(row,'OWNER_UID')` → `_s(row,'OWNER_UID_X')` | TEST_GAP | `owner_id` becomes `''`; no test asserts it. Exposing input: `convert_contact(legacy_row())["owner_id"] == "U0000001"` (mutant: `""`). |
| 19 | SCH-03 | migrated.py (node 283) | `'name': _s(row,'OPP_NM')` → `_s(row,'OPP_NM_X')` | TEST_GAP | Opportunity `name` becomes `''`; tests check the key set and stage/amount/date logic but never the `name` value. Exposing input: `convert_opportunity(legacy_row())["name"] == "Fleet Renewal"` (mutant: `""`). |
| 20 | VAL-01 | migrated.py (node 140) | `_date_ge`: `if a == SENTINEL or b == SENTINEL:` → `if a != SENTINEL or ...` | TEST_GAP | `_date_ge` is reached only when `close != SENTINEL`, so the mutant returns False on every reachable call and rule OPP-007 (E3007 WARN) fires for *every* non-sentinel close date, including future ones. No test inserts a valid future close date. Exposing input: `validate(ok_insert(CLOSE_DT="20261231"), None, "INSERT", "20260901") == []` (mutant: `["E3007"]`). |
| 21 | VAL-02 | migrated.py (node 59) | signature default `event='INSERT'` → `event='INSERT_X'` | EQUIVALENT | The default matters only when `event` is omitted. `'INSERT_X'` fails both event comparisons; failing `== 'INSERT'` merely skips `old = {}`, and in VAL-02 `old` is read only inside the `event == 'UPDATE'` branch (also not taken). Fuzz over old/event/hold/limit combinations found 0 output differences. |
| 22 | VAL-02 | migrated.py (node 123) | `if event == 'INSERT': old = {}` → `if event == 'INSERT_X':` | EQUIVALENT | Clearing `old` on INSERT is unobservable in VAL-02: `old` is only consulted under `event == 'UPDATE'`, where the mutated condition is equally false. Fuzz over the same grid found 0 differences. (Note: the twin mutation in VAL-03 is *not* equivalent — see #25.) |
| 23 | VAL-02 | migrated.py (node 233) | `typ not in ('C','P','R','X')` → `('C','P','R_X','X')` | TEST_GAP | Account type `'R'` (a legal legacy value) now raises E1002. Tests use only `'C'` (valid) and `'Z'` (invalid). Exposing input: `validate(ok_record(ACCT_TYP="R"), None, "INSERT", TODAY) == []` (mutant: `["E1002"]`). Types `'P'`/`'X'` are equally untested. |
| 24 | VAL-03 | migrated.py (node 55) | signature default `event='INSERT'` → `event='INSERT_X'` | TEST_GAP | Unlike VAL-02, VAL-03 gates rule ORD-005 (E5005, product-active LOOKUP) on `event == 'INSERT'`, so calls that rely on the spec'd default (`event: str = "INSERT"` in target_spec.md) skip E5005. Every test passes `event` positionally. Exposing input: `validate(line(PROD_ID="P00000002"), None, tables=tables(), table="ORD_LINE") == ["E5005"]` with event omitted (mutant: `[]`). |
| 25 | VAL-03 | migrated.py (node 245) | `disc >= 0 and disc <= 100` → `disc >= 0 and disc < 100` | TEST_GAP | Boundary: `DISC_PCT == 100` is legal (ORD-001 is inclusive) but the mutant rejects it; tests probe 101, −1, and 20 only. Exposing input: `validate(header(DISC_PCT=100), None, "INSERT", tables(), "ORD_HEADER") == []` (mutant: `["E5001"]`). |
| 26 | WFL-01 | migrated.py (node 119) | Q→close_lost transition to-state `'L'` → `'L_X'` | TEST_GAP | The Q→L close_lost row is only ever exercised with a blocked guard (`LOST_RSN=""` → NOMATCH); no test fires it successfully. Exposing input: `fire("Q", "close_lost", opp(STAT_CD="Q", LOST_RSN="CM"))["state"] == "L"` (mutant: `"L_X"`). |
| 27 | WFL-01 | migrated.py (node 277) | Q→close_lost action `('set','STAGE_PCT','0')` → `'0_X'` | TEST_GAP | Same untested transition as #26, on its `set` payload. Exposing input: same call, `res["record"]["STAGE_PCT"] == "0"` (mutant: `"0_X"`). |
| 28 | WFL-03 | migrated.py (node 300) | matched-fire return: key `'record'` → `'record_X'` | TEST_GAP | The spec requires "exactly the keys `state`, `record`, `audits`, `notifies`, `matched`", but no test ever reads `res["record"]` (or the key set) on a matched fire — only state/audits/notifies/matched. Exposing input: `set(fire("E","approve",order(),tables(acct())).keys()) == {"state","record","audits","notifies","matched"}` (mutant: has `record_X`). |

## Counts by classification

| Classification | Count |
|----------------|------:|
| EQUIVALENT | 9 |
| TEST_GAP | 17 |
| HARNESS_ARTIFACT | 2 |
| UNRESOLVED | 0 |
| **Total** | **28** |

Effective mutation score counting equivalent mutants and harness artifacts as
non-actionable: 335 killed / (363 − 9 − 2) = 335/352 ≈ **95.2%** (raw 92.3%).

## Recommended test additions (for a future benchmark revision — not applied)

Grouped by survivor; each line gives the concrete assertion that would kill the mutant.

1. **ERR-02 (#6)** — transient-exhaustion shape:
   `out = call_with_retry({"url":"u","retry":1,"timeout_ms":5}, always_transient)` then
   `assert set(out.keys()) == {"ok","attempts","result","error"} and out["result"] is None`.
2. **INT-02 (#7)** — record width with blank date:
   `assert len(mod.format_account(acct(CREATE_DT=""))) == 77`.
3. **RBC-01 (#11)** — ADMIN override path:
   `assert mod.can(user("U0000001","ADMIN","T01"), "READ", "ACCT_MASTER", rec("U0000009","T09"), rows) is True`
   (plus an ADMIN DELETE on a live foreign record).
4. **RBC-01 (#12)** — blank DEL_FLG on DELETE:
   `assert mod.can(MGR, "DELETE", "OPP_MASTER", rec("U0000003","T01", del_flg=""), rows) is True`.
5. **RBC-02 (#13)** — granting OWN scope:
   `assert mod.can(user("U0000003","REP","T01"), "UPDATE", "OPP_MASTER", rec("U0000003","T01"), rows) is True`.
6. **SCH-01 (#15)** — verbatim mapping completeness:
   extend `test_verbatim_string_fields` with `assert out["owner_id"] == "U0000001"`
   (and, for symmetry, `out["sic_code"] == "3714"`).
7. **SCH-02 (#16–18)** — value assertions for the unchecked fields:
   `out = convert_contact(legacy_row()); assert out["first_name"] == "Dana"; assert out["last_name"] == "Whitfield"; assert out["phone"] == "+1-555-0142"; assert out["owner_id"] == "U0000001"`.
8. **SCH-03 (#19)** — `assert convert_opportunity(legacy_row())["name"] == "Fleet Renewal"`.
9. **VAL-01 (#20)** — OPP-007 pass path:
   `assert mod.validate(ok_insert(CLOSE_DT="20261231"), None, "INSERT", TODAY) == []`
   (and the boundary `CLOSE_DT == TODAY` also expecting `[]`).
10. **VAL-02 (#23)** — remaining legal account types:
    `for t in ("P","R","X"): assert mod.validate(ok_record(ACCT_TYP=t), None, "INSERT", TODAY) == []`.
11. **VAL-03 (#24)** — spec'd default event:
    `assert codes(mod.validate(line(PROD_ID="P00000002"), tables=tables(), table="ORD_LINE")) == ["E5005"]` (event omitted).
12. **VAL-03 (#25)** — inclusive discount boundary:
    `assert mod.validate(header(DISC_PCT=100), None, "INSERT", tables(), "ORD_HEADER") == []`.
13. **WFL-01 (#26, #27)** — successful Q→L close:
    `res = mod.fire("Q", "close_lost", opp(STAT_CD="Q", LOST_RSN="CM")); assert res["state"] == "L"; assert res["record"]["STAGE_PCT"] == "0"; assert res["audits"] == ["OPP_LOST"]`.
14. **WFL-03 (#28)** — matched-fire return shape:
    `res = mod.fire("E", "approve", order(), tables(acct())); assert set(res.keys()) == {"state","record","audits","notifies","matched"}; assert res["record"] == order()`.

### Notes

- The two HARNESS_ARTIFACT survivors (BIZ-01/BIZ-02 exception-string format) are judged
  acceptable as-is: both specs define the exception contract through the `code` and
  `message` attributes, which the tests do assert exactly; `str(exc)` formatting is
  incidental. If a future revision wants to pin it, add
  `assert str(exc.value) == "E1004: Cannot release credit hold with zero credit limit"`.
- The RBC-03 equivalence (#14) holds only because `policy.json` is part of the same
  fixed deliverable and always carries the key; a revision that lets solvers author
  `policy.json` freely should add a test with the key absent to pin the deny-safe default.
- VAL-02 #21/#22 vs. VAL-03 #24 illustrate that the identical mutation can be equivalent
  in one rule set and behavior-changing in another; classification was done per case, not
  per pattern.
