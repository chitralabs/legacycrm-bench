"""AUD-02 reference solution: per-column audit event emitter.

Preserves SYSTEM_OVERVIEW.md §8 semantics: one event per changed audited column
(audit_config.cfg file order), OLD_VAL/NEW_VAL stringified, AUD_EVENT field names,
injected timestamp (no wall clock).
"""

# audit_config.cfg, baked in verbatim (file order per table).
AUDITED = {
    "ACCT_MASTER": ["CRED_HOLD", "CRED_LIMIT", "OWNER_UID"],
    "OPP_MASTER": ["STAT_CD", "AMT", "OWNER_UID"],
    "CASE_MASTER": ["STAT_CD", "SEV_CD"],
    "ORD_HEADER": ["STAT_CD", "DISC_PCT"],
    "USR_MASTER": ["ROLE_ID", "ACTIVE_FLG"],
}

# Primary-key column per table (legacy_schema.sql).
PK = {
    "ACCT_MASTER": "ACCT_ID",
    "OPP_MASTER": "OPP_ID",
    "CASE_MASTER": "CASE_ID",
    "ORD_HEADER": "ORD_ID",
    "USR_MASTER": "USR_ID",
}


def _s(d, key):
    v = d.get(key, "")
    return "" if v is None else str(v)


def emit_audits(table, old, new, user, ts):
    events = []
    columns = AUDITED.get(table, [])
    if not columns:
        return events
    pk_col = PK[table]
    ent_id = _s(new, pk_col) or _s(old, pk_col)
    for col in columns:
        old_val = _s(old, col)
        new_val = _s(new, col)
        if old_val != new_val:
            events.append({
                "EVT_TS": ts,
                "EVT_CD": "COL_UPD",
                "USR_ID": user,
                "ENT_NAME": table,
                "ENT_ID": ent_id,
                "OLD_VAL": old_val,
                "NEW_VAL": new_val,
            })
    return events
