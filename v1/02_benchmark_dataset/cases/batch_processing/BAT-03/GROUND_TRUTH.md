# BAT-03 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** by tracing
`legacy/dw_export.crms` under the CRMScript semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §4, §7). No LLM output was used to produce expectations.
Test rows are synthetic strings `REC00000`, `REC00001`, … constructed in-test.

Trace of the script: `batch` accumulates `rec & CHR(10)` per row and `n` counts rows;
`IF n = 500` posts and resets both; after the loop `IF n > 0` posts the remainder.
Chunk-count derivations for the required row counts:

1. **0 rows**: loop body never runs → n stays 0 → final `IF n > 0` FALSE → no `send`
   call at all; return value 0 (no records counted).
2. **1 row**: loop appends once (n=1, never hits 500) → final post fires once with
   payload `"REC00000\n"` → exactly 1 call; returns 1.
3. **499 rows**: n reaches 499, never 500 → single final post with 499 records;
   returns 499.
4. **500 rows**: on the 500th append `IF n = 500` fires → post inside the loop; batch
   and n reset to empty/0; loop ends; final `IF n > 0` FALSE → **exactly one** call
   (a naive "flush after loop" migration would send a second, empty payload — forbidden);
   returns 500.
5. **501 rows**: one in-loop post at row 500 (records 0–499), then n=1 remains → final
   post with 1 record (row 500) → calls of sizes [500, 1]; returns 501.
6. **1000 rows**: in-loop posts at rows 500 and 1000 → sizes [500, 500]; after the second
   post n=0 → no third call; returns 1000.
7. Payload format: `batch = batch & rec & CHR(10)` with CHR(10) = newline → every record
   is followed by exactly one "\n", so a k-record payload equals
   `"".join(r + "\n" for r in chunk)`, ends with "\n", and `payload.split("\n")` has k
   non-empty parts plus one trailing empty part.
8. Order: FOR EACH appends in iteration order and posts never reorder → the first payload
   carries rows 0–499 (first record `REC00000`, last `REC00499`), the second starts at
   `REC00500`; concatenating the records of all payloads reproduces the input row list.
9. Return value: the modern function reports records sent; every row is appended exactly
   once and every non-empty batch is posted exactly once → returns len(rows) for all
   sizes above.
10. Negative expectation: no payload is ever the empty string (cases 1 and 4 above are
    where naive implementations emit one).
