"""AUD-03 reference solution: legacy AUD_EVENT rows -> modern append-only event store.

Preserves SYSTEM_OVERVIEW.md §8 semantics: append-only audit storage, canonical EVT_ID
order, verbatim value preservation; EVT_TS re-sliced to ISO-8601 (no clock reads).
"""


def migrate_event(row):
    ts = row["EVT_TS"]
    iso = f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}T{ts[8:10]}:{ts[10:12]}:{ts[12:14]}"
    return {
        "evt_id": int(row["EVT_ID"]),
        "ts": iso,
        "code": row["EVT_CD"],
        "user_id": row["USR_ID"],
        "entity": row["ENT_NAME"],
        "entity_id": row["ENT_ID"],
        "old_val": row["OLD_VAL"],
        "new_val": row["NEW_VAL"],
    }


class AuditStore:
    """Append-only event store: append() is the sole mutator."""

    def __init__(self):
        self._events = []
        self._ids = set()

    def append(self, event):
        self._events.append(dict(event))
        self._ids.add(event.get("evt_id"))

    def events(self):
        return [dict(e) for e in self._events]

    def __len__(self):
        return len(self._events)

    def _has_id(self, evt_id):
        return evt_id in self._ids


def migrate(rows, store=None):
    if store is None:
        store = AuditStore()
    for row in sorted(rows, key=lambda r: int(r["EVT_ID"])):
        event = migrate_event(row)
        if not store._has_id(event["evt_id"]):
            store.append(event)
    return store
