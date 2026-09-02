"""RIN-03 reference solution: load legacy rows into the FK-enforced modern schema.

Enables PRAGMA foreign_keys=ON, applies modern_schema.sql (located next to this file),
inserts live rows parents-first, drops legacy-only columns (DEL_FLG etc.), and lets
sqlite3.IntegrityError propagate for dirty data (orphans must fail loudly).
"""
from pathlib import Path

COLUMNS = {
    "ACCT_MASTER": ["ACCT_ID", "ACCT_NM", "ACCT_TYP", "REGION_CD", "ANN_REV",
                    "CURR_CD", "CRED_LIMIT", "CRED_HOLD", "CREATE_DT"],
    "CONT_MASTER": ["CONT_ID", "ACCT_ID", "FRST_NM", "LAST_NM", "EMAIL_TX",
                    "PREF_CH", "OPTOUT_FLG"],
    "ORD_HEADER": ["ORD_ID", "ACCT_ID", "ORD_DT", "STAT_CD", "DISC_PCT", "TOT_AMT"],
    "ORD_LINE": ["ORD_ID", "LINE_NO", "PROD_ID", "QTY", "UNIT_PRC", "EXT_AMT"],
}
LOAD_ORDER = ["ACCT_MASTER", "CONT_MASTER", "ORD_HEADER", "ORD_LINE"]


def _is_live(row):
    v = row.get("DEL_FLG", "")
    return ("" if v is None else str(v)) != "Y"  # blank means 'N'


def load(conn, tables):
    conn.execute("PRAGMA foreign_keys = ON")
    schema = (Path(__file__).resolve().parent / "modern_schema.sql").read_text()
    conn.executescript(schema)
    counts = {}
    for table in LOAD_ORDER:
        cols = COLUMNS[table]
        sql = "INSERT INTO {} ({}) VALUES ({})".format(
            table, ", ".join(cols), ", ".join("?" for _ in cols))
        n = 0
        for row in tables.get(table, []):
            if not _is_live(row):
                continue
            conn.execute(sql, [row.get(c) for c in cols])
            n += 1
        counts[table] = n
    conn.commit()
    return counts
