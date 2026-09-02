"""RIN-03 acceptance tests. Expected values derived by hand in ../GROUND_TRUTH.md."""
import re
import sqlite3

import pytest
import case_lib


@pytest.fixture()
def mod():
    return case_lib.load_solution_module(__file__, "migrated")


@pytest.fixture()
def schema_sql():
    return case_lib.solution_file(__file__, "modern_schema.sql").read_text()


@pytest.fixture()
def conn(schema_sql):
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys = ON")
    c.executescript(schema_sql)
    yield c
    c.close()


def ins_acct(c, acct_id="A00000001"):
    c.execute("INSERT INTO ACCT_MASTER (ACCT_ID, ACCT_NM) VALUES (?, ?)",
              (acct_id, "Acct " + acct_id))


def ins_ord(c, ord_id="D00000001", acct_id="A00000001"):
    c.execute("INSERT INTO ORD_HEADER (ORD_ID, ACCT_ID, STAT_CD) VALUES (?, ?, 'E')",
              (ord_id, acct_id))


def clean_tables():
    return {
        "ACCT_MASTER": [
            {"ACCT_ID": "A00000001", "ACCT_NM": "Alpha", "DEL_FLG": "N"},
            {"ACCT_ID": "A00000002", "ACCT_NM": "Beta", "DEL_FLG": "N"},
        ],
        "CONT_MASTER": [
            {"CONT_ID": "K00000001", "ACCT_ID": "A00000001", "LAST_NM": "Vail",
             "DEL_FLG": "N"},
        ],
        "ORD_HEADER": [
            {"ORD_ID": "D00000001", "ACCT_ID": "A00000002", "STAT_CD": "E",
             "TOT_AMT": "100.00", "DEL_FLG": "N"},
        ],
        "ORD_LINE": [
            {"ORD_ID": "D00000001", "LINE_NO": 1, "PROD_ID": "P00000001",
             "QTY": 2, "UNIT_PRC": "50.00", "EXT_AMT": "100.00", "DEL_FLG": "N"},
        ],
    }


def test_schema_creates_all_four_tables(conn):
    names = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"ACCT_MASTER", "CONT_MASTER", "ORD_HEADER", "ORD_LINE"} <= names


def test_orphan_contact_insert_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO CONT_MASTER (CONT_ID, ACCT_ID, LAST_NM) VALUES "
            "('K00000001', 'A00000404', 'Ghost')")


def test_orphan_order_insert_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO ORD_HEADER (ORD_ID, ACCT_ID) VALUES ('D00000001', 'A00000404')")


def test_orphan_line_insert_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO ORD_LINE (ORD_ID, LINE_NO) VALUES ('D00000404', 1)")


def test_delete_account_with_orders_restricted(conn):
    ins_acct(conn)
    ins_ord(conn)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM ACCT_MASTER WHERE ACCT_ID = 'A00000001'")


def test_delete_account_with_contacts_restricted(conn):
    ins_acct(conn)
    conn.execute("INSERT INTO CONT_MASTER (CONT_ID, ACCT_ID, LAST_NM) VALUES "
                 "('K00000001', 'A00000001', 'Vail')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM ACCT_MASTER WHERE ACCT_ID = 'A00000001'")


def test_delete_header_cascades_lines(conn):
    ins_acct(conn)
    ins_ord(conn)
    conn.execute("INSERT INTO ORD_LINE (ORD_ID, LINE_NO) VALUES ('D00000001', 1)")
    conn.execute("INSERT INTO ORD_LINE (ORD_ID, LINE_NO) VALUES ('D00000001', 2)")
    conn.execute("DELETE FROM ORD_HEADER WHERE ORD_ID = 'D00000001'")
    assert conn.execute("SELECT COUNT(*) FROM ORD_LINE").fetchone()[0] == 0


def test_declared_fk_actions_not_weakened(conn):
    # Security: the delete actions are declared exactly as documented, not defaulted
    # or widened (a CASCADE on account FKs would silently destroy dependents).
    def actions(table):
        return {(r[2], r[3], r[4], r[6]) for r in
                conn.execute(f"PRAGMA foreign_key_list({table})")}
    assert ("ACCT_MASTER", "ACCT_ID", "ACCT_ID", "RESTRICT") in actions("CONT_MASTER")
    assert ("ACCT_MASTER", "ACCT_ID", "ACCT_ID", "RESTRICT") in actions("ORD_HEADER")
    assert ("ORD_HEADER", "ORD_ID", "ORD_ID", "CASCADE") in actions("ORD_LINE")


def test_duplicate_account_pk_rejected(conn):
    ins_acct(conn)
    with pytest.raises(sqlite3.IntegrityError):
        ins_acct(conn)


def test_duplicate_composite_line_key_rejected(conn):
    ins_acct(conn)
    ins_ord(conn)
    conn.execute("INSERT INTO ORD_LINE (ORD_ID, LINE_NO) VALUES ('D00000001', 1)")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO ORD_LINE (ORD_ID, LINE_NO) VALUES ('D00000001', 1)")


def test_no_soft_delete_column_survives(schema_sql):
    # Soft delete is retired in the modern schema (target_spec).
    assert not re.search(r"\bDEL_FLG\b", schema_sql)


def test_load_clean_fixture_succeeds_with_counts(mod):
    c = sqlite3.connect(":memory:")
    counts = mod.load(c, clean_tables())
    assert counts == {"ACCT_MASTER": 2, "CONT_MASTER": 1,
                      "ORD_HEADER": 1, "ORD_LINE": 1}
    assert c.execute("SELECT ACCT_ID FROM ORD_HEADER").fetchone()[0] == "A00000002"
    c.close()


def test_load_excludes_soft_deleted_rows(mod):
    tables = clean_tables()
    tables["ACCT_MASTER"].append(
        {"ACCT_ID": "A00000009", "ACCT_NM": "Gone", "DEL_FLG": "Y"})
    c = sqlite3.connect(":memory:")
    counts = mod.load(c, tables)
    assert counts["ACCT_MASTER"] == 2
    assert c.execute("SELECT COUNT(*) FROM ACCT_MASTER WHERE ACCT_ID='A00000009'"
                     ).fetchone()[0] == 0
    c.close()


def test_load_orphan_contact_fails_loudly(mod):
    # Contact points at a soft-deleted account: the parent is not loaded, so the
    # child insert must raise (never be silently dropped or inserted).
    tables = clean_tables()
    tables["ACCT_MASTER"][0]["DEL_FLG"] = "Y"  # A00000001, parent of K00000001
    c = sqlite3.connect(":memory:")
    with pytest.raises(sqlite3.IntegrityError):
        mod.load(c, tables)
    c.close()


def test_load_enables_foreign_keys_pragma(mod):
    c = sqlite3.connect(":memory:")
    mod.load(c, clean_tables())
    assert c.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    c.close()
