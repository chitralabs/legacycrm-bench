#!/usr/bin/env python3
"""Deterministic synthetic seed data for LegacyCRM-Bench (Meridian CRM 4.2).

Provenance: all records are fictional and generated from the fixed word lists below with
random seed 20260901. No real personal, customer, or employer data is used. Re-running this
script reproduces byte-identical CSVs (dataset card: 02_benchmark_dataset/DATASET_CARD.md).
"""
import csv
import random
from pathlib import Path

SEED = 20260901
OUT = Path(__file__).resolve().parent.parent / "02_benchmark_dataset" / "legacy_system" / "seed_data"

FIRST = ["Avery", "Jordan", "Riley", "Casey", "Morgan", "Quinn", "Rowan", "Sage", "Taylor", "Emery",
         "Harper", "Kendall", "Logan", "Parker", "Reese", "Skyler", "Dakota", "Finley", "Hayden", "Marlow"]
LAST = ["Calder", "Whitfield", "Ostrander", "Bellamy", "Kirkwood", "Ashford", "Draper", "Ellison",
        "Fairbank", "Granger", "Holloway", "Iverson", "Jennings", "Kessler", "Lockhart", "Mercer",
        "Norwood", "Oakes", "Pemberton", "Quimby"]
ORG_A = ["Northwind", "Bluepeak", "Cascade", "Ironbridge", "Silverline", "Redwood", "Halcyon",
         "Vantage", "Crestway", "Lakemont", "Stonefield", "Brighthaven", "Copperleaf", "Duneside"]
ORG_B = ["Logistics", "Manufacturing", "Analytics", "Foods", "Robotics", "Textiles", "Energy",
         "Medical", "Holdings", "Freight", "Materials", "Systems"]
REGIONS = ["NAM", "EMA", "APA", "LAT"]
TEAMS = ["T01", "T02", "T03", "T04"]
CURRS = ["", "", "", "EUR", "GBP", "JPY"]  # blank = USD (legacy convention), weighted
LOST = ["PR", "CM", "NB", "TM", "OT"]
FAMS = ["CORE", "ADDON", "SVC", "HW"]

def ymd(rng, y0=2018, y1=2025):
    y = rng.randint(y0, y1); m = rng.randint(1, 12); d = rng.randint(1, 28)
    return f"{y:04d}{m:02d}{d:02d}"

def money(rng, lo, hi):
    return f"{rng.randint(lo * 100, hi * 100) / 100:.2f}"

def main():
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)

    users, roles = [], ["ADMIN", "MGR", "REP", "SUPP", "AUDIT"]
    for i in range(1, 25):
        uid = f"U{i:07d}"
        role = roles[0] if i == 1 else (roles[1] if i <= 4 else (roles[2] if i <= 16 else (roles[3] if i <= 21 else roles[4])))
        users.append({"USR_ID": uid, "USR_NM": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                      "ROLE_ID": role, "TEAM_CD": rng.choice(TEAMS),
                      "MGR_UID": "U0000001" if role != "ADMIN" else "",
                      "ACTIVE_FLG": "Y" if i != 20 else "N", "DEL_FLG": "N"})

    accts = []
    for i in range(1, 61):
        aid = f"A{i:08d}"
        typ = rng.choice("CCCPPRX")
        owner = rng.choice(users[1:16])
        accts.append({"ACCT_ID": aid, "ACCT_NM": f"{rng.choice(ORG_A)} {rng.choice(ORG_B)}",
                      "ACCT_TYP": typ, "SIC_CD": f"{rng.randint(1000, 8999)}",
                      "REGION_CD": rng.choice(REGIONS), "ANN_REV": money(rng, 100000, 90000000),
                      "CURR_CD": rng.choice(CURRS), "OWNER_UID": owner["USR_ID"],
                      "TEAM_CD": owner["TEAM_CD"], "CRED_LIMIT": money(rng, 5000, 500000),
                      "CRED_HOLD": "Y" if rng.random() < 0.08 else "N",
                      "CREATE_DT": ymd(rng), "UPD_DT": ymd(rng, 2024, 2025),
                      "DEL_FLG": "Y" if rng.random() < 0.05 else "N"})

    conts = []
    for i in range(1, 121):
        cid = f"K{i:08d}"
        acct = rng.choice(accts)
        first, last = rng.choice(FIRST), rng.choice(LAST)
        # ~4% orphans by design (dangling ACCT_ID) to exercise integrity tasks
        acct_id = acct["ACCT_ID"] if rng.random() > 0.04 else f"A9{rng.randint(1000000, 9999999)}"
        conts.append({"CONT_ID": cid, "ACCT_ID": acct_id, "FRST_NM": first, "LAST_NM": last,
                      "EMAIL_TX": f"{first.lower()}.{last.lower()}@example.com" if rng.random() > 0.1 else "",
                      "PHONE_TX": f"+1-555-{rng.randint(100, 999)}-{rng.randint(1000, 9999)}",
                      "PREF_CH": rng.choice(["E", "E", "P", "M", ""]),
                      "OPTOUT_FLG": "Y" if rng.random() < 0.15 else "N",
                      "OWNER_UID": acct["OWNER_UID"], "TEAM_CD": acct["TEAM_CD"],
                      "CREATE_DT": ymd(rng), "DEL_FLG": "Y" if rng.random() < 0.05 else "N"})

    opps = []
    for i in range(1, 81):
        oid = f"O{i:08d}"
        acct = rng.choice(accts)
        stat = rng.choice("PPQQNNWL")
        pct = {"P": 10, "Q": 25, "N": 60, "W": 100, "L": 0}[stat]
        opps.append({"OPP_ID": oid, "ACCT_ID": acct["ACCT_ID"],
                     "OPP_NM": f"{acct['ACCT_NM']} {rng.choice(['Renewal', 'Expansion', 'New Business', 'Upsell'])}",
                     "STAT_CD": stat, "STAGE_PCT": str(pct),
                     "AMT": money(rng, 1000, 900000), "CURR_CD": rng.choice(CURRS),
                     "CLOSE_DT": ymd(rng, 2024, 2026) if stat in "WL" else ("00000000" if rng.random() < 0.3 else ymd(rng, 2026, 2027)),
                     "OWNER_UID": acct["OWNER_UID"], "TEAM_CD": acct["TEAM_CD"],
                     "LOST_RSN": rng.choice(LOST) if stat == "L" else "",
                     "CREATE_DT": ymd(rng), "UPD_DT": ymd(rng, 2024, 2025), "DEL_FLG": "N"})

    cases = []
    for i in range(1, 71):
        acct = rng.choice(accts)
        cont = rng.choice(conts)
        stat = rng.choice("NNAAPRX")
        cases.append({"CASE_ID": f"C{i:08d}", "ACCT_ID": acct["ACCT_ID"], "CONT_ID": cont["CONT_ID"],
                      "SEV_CD": rng.choice("123334"), "STAT_CD": stat,
                      "SUBJ_TX": rng.choice(["Login failure after upgrade", "Invoice mismatch on order",
                                             "Report export truncated", "Duplicate contact records",
                                             "Integration timeout to ERP", "Password reset loop"]),
                      "OPEN_DT": ymd(rng, 2025, 2026),
                      "RES_DT": ymd(rng, 2025, 2026) if stat in "RX" else "00000000",
                      "OWNER_UID": acct["OWNER_UID"] if stat != "N" else "",
                      "TEAM_CD": acct["TEAM_CD"], "ESC_FLG": "Y" if rng.random() < 0.1 else "N",
                      "DEL_FLG": "N"})

    prods = []
    for i in range(1, 31):
        prods.append({"PROD_ID": f"P{i:08d}", "PROD_NM": f"Meridian {rng.choice(['Suite', 'Module', 'Connector', 'Pack'])} {i}",
                      "FAMILY_CD": rng.choice(FAMS), "LIST_PRC": money(rng, 50, 20000),
                      "ACTIVE_FLG": "Y" if rng.random() > 0.2 else "N",
                      "EOL_DT": "00000000" if rng.random() > 0.25 else ymd(rng, 2024, 2027),
                      "DEL_FLG": "N"})

    ords, lines = [], []
    for i in range(1, 51):
        did = f"D{i:08d}"
        acct = rng.choice(accts)
        stat = rng.choice("EEAASIX")
        disc = rng.choice([0, 0, 0, 5, 10, 15, 25])
        total = 0.0
        nlines = rng.randint(1, 5)
        for ln in range(1, nlines + 1):
            prod = rng.choice(prods)
            qty = rng.randint(1, 20)
            unit = float(prod["LIST_PRC"])
            ext = round(qty * unit, 2)
            total += ext
            lines.append({"ORD_ID": did, "LINE_NO": str(ln), "PROD_ID": prod["PROD_ID"],
                          "QTY": str(qty), "UNIT_PRC": f"{unit:.2f}", "EXT_AMT": f"{ext:.2f}",
                          "DEL_FLG": "N"})
        tot = round(total * (100 - disc) / 100, 2)
        ords.append({"ORD_ID": did, "ACCT_ID": acct["ACCT_ID"], "ORD_DT": ymd(rng, 2024, 2026),
                     "STAT_CD": stat, "CURR_CD": acct["CURR_CD"], "DISC_PCT": f"{disc:.2f}",
                     "TOT_AMT": f"{tot:.2f}", "OWNER_UID": acct["OWNER_UID"], "DEL_FLG": "N"})

    acts = []
    for i in range(1, 101):
        ent = rng.choice([("ACCT_MASTER", rng.choice(accts)["ACCT_ID"]),
                          ("OPP_MASTER", rng.choice(opps)["OPP_ID"]),
                          ("CASE_MASTER", rng.choice(cases)["CASE_ID"])])
        acts.append({"ACT_ID": f"T{i:08d}", "ENT_NAME": ent[0], "ENT_ID": ent[1],
                     "ACT_TYP": rng.choice("CEMK"), "ACT_DT": ymd(rng, 2025, 2026),
                     "DONE_FLG": rng.choice("YYN"), "NOTES_TX": "Follow-up recorded.",
                     "OWNER_UID": rng.choice(users)["USR_ID"], "DEL_FLG": "N"})

    auds = []
    for i in range(1, 41):
        opp = rng.choice(opps)
        auds.append({"EVT_ID": str(i), "EVT_TS": ymd(rng, 2025, 2026) + f"{rng.randint(0,23):02d}{rng.randint(0,59):02d}{rng.randint(0,59):02d}",
                     "EVT_CD": rng.choice(["OPP_QUAL", "OPP_WON", "OPP_LOST", "CASE_ESC", "ORD_APPR"]),
                     "USR_ID": rng.choice(users)["USR_ID"], "ENT_NAME": "OPP_MASTER",
                     "ENT_ID": opp["OPP_ID"], "OLD_VAL": "P", "NEW_VAL": opp["STAT_CD"]})

    for name, rows in [("ACCT_MASTER", accts), ("CONT_MASTER", conts), ("OPP_MASTER", opps),
                       ("CASE_MASTER", cases), ("PROD_MASTER", prods), ("ORD_HEADER", ords),
                       ("ORD_LINE", lines), ("ACT_LOG", acts), ("USR_MASTER", users),
                       ("AUD_EVENT", auds)]:
        with open(OUT / f"{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print(f"{name}: {len(rows)} rows")

if __name__ == "__main__":
    main()
