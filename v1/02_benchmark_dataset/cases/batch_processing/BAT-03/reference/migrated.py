"""BAT-03 reference solution: dw_export.crms chunked transmission migrated to Python.

Preserves legacy semantics (SYSTEM_OVERVIEW.md §4 + dw_export.crms): chunks of exactly
500 records posted via the injected send(), records each followed by one newline
(CHR(10)), final partial chunk sent iff non-empty, never an empty payload.
"""

CHUNK_SIZE = 500


def export_chunks(rows, send):
    batch = []
    sent = 0
    for rec in rows:
        batch.append(str(rec))
        sent += 1
        if len(batch) == CHUNK_SIZE:  # IF n = 500 THEN post and reset
            send("".join(r + "\n" for r in batch))
            batch = []
    if batch:  # IF n > 0 THEN post the final partial chunk
        send("".join(r + "\n" for r in batch))
    return sent
