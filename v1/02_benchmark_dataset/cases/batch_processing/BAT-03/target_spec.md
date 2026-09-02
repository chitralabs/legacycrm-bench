# BAT-03 Target Specification

Migrate the **chunked-transmission logic** of the nightly data-warehouse export
`legacy/dw_export.crms` (language and batch semantics in `legacy/SEMANTICS_EXCERPT.md`)
to the modern platform as **one Python module** `migrated.py`. Record *formatting*
(FIXED/ZPAD layout) is out of scope for this case — the caller supplies already-formatted
record strings; this case migrates the batching loop around `CALL HTTPPOST`.

## Required interface

```python
def export_chunks(rows: list[str], send) -> int: ...
```

- `rows`: formatted export records (one string per record, no trailing newline of their
  own), in export order.
- `send`: injected callable replacing `CALL HTTPPOST('dw_accounts', batch)`;
  `send(payload)` transmits one chunk. The module performs no network I/O itself.
- Returns the total number of **records** sent (the legacy `n` counter summed over all
  chunks), which must equal `len(rows)`.

## Required behavior (from dw_export.crms)

1. Records are accumulated in input order into a chunk of **exactly 500** records; when
   the 500th record is appended (`IF n = 500`), the chunk is sent immediately and the
   accumulator resets.
2. After the loop, the **final partial chunk is sent iff it is non-empty**
   (`IF n > 0 THEN CALL HTTPPOST(...)`). Consequences that must hold exactly:
   - 0 rows → `send` is never called;
   - 1–500 rows → exactly one `send` call;
   - 501–1000 rows → exactly two calls (500 + remainder), and for exactly 1000 rows the
     second call carries 500 with **no third empty call** (the accumulator is empty when
     the loop ends).
3. Payload format (`batch = batch & rec & CHR(10)`): each record is followed by one
   newline — the payload is `rec1 + "\n" + rec2 + "\n" + ... + recN + "\n"` (trailing
   newline after the last record; no other separators, no header, no record count — the
   legacy DW infers the count from the rows).
4. Chunk boundaries preserve order: the first `send` carries rows 0–499, the second rows
   500 onward, etc.; concatenating all payloads' records reproduces `rows` exactly.
5. An empty payload is never sent.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
