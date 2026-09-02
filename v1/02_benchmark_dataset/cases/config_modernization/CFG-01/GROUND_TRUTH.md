# CFG-01 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** by reading each
DICT_TYPE=COLUMN row of `legacy/data_dictionary.csv` and splitting its MEANING on `;` and
`=`, per the conventions in `legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §1). No LLM
output was used. Derivations:

1. ACCT_MASTER.ACCT_TYP ← "C=Customer;P=Prospect;R=Partner;X=Inactive" →
   {C: Customer, P: Prospect, R: Partner, X: Inactive}.
2. CONT_MASTER.PREF_CH ← "E=email;P=phone;M=mail;blank=E" → {E: email, P: phone, M: mail}.
   "blank=E" is a storage default (§1), not a code → excluded (negative expectation).
3. OPP_MASTER.STAT_CD ← "P=Prospecting(10%);Q=Qualified(25%);N=Negotiation(60%);
   W=Closed-Won(100%);L=Closed-Lost(0%)" → parenthesized stage-percent annotations stripped
   → {P: Prospecting, Q: Qualified, N: Negotiation, W: Closed-Won, L: Closed-Lost}.
4. OPP_MASTER.LOST_RSN ← "PR=price;CM=competitor;NB=no budget;TM=timing;OT=other" →
   {PR: price, CM: competitor, NB: "no budget", TM: timing, OT: other} (space in "no budget"
   preserved).
5. CASE_MASTER.SEV_CD ← "1=Critical(4h target);2=High(8h);3=Normal(24h);4=Low(72h)" →
   response-time annotations stripped → {1: Critical, 2: High, 3: Normal, 4: Low}.
6. CASE_MASTER.STAT_CD ← "N=New;A=Assigned;P=Pending-Customer;R=Resolved;X=Closed" →
   hyphen in "Pending-Customer" preserved.
7. ORD_HEADER.STAT_CD ← "E=Entered;A=Approved;S=Shipped;I=Invoiced;X=Cancelled".
8. ACT_LOG.ACT_TYP ← "C=Call;E=Email;M=Meeting;K=Task".
9. Excluded rows (hallucination negatives): ACCT_MASTER.CURR_CD (ISO-4217 reference set, not
   an enumerated code table), ACCT_MASTER.CRED_HOLD and CONT_MASTER.OPTOUT_FLG (Y/N boolean
   conventions), ALL.DEL_FLG, ALL.*_DT (conventions) — none may appear as top-level keys, so
   the top level has exactly the eight keys of entries 1–8.
10. No invented codes: each map's key set equals exactly the codes listed in entries 1–8
    (asserted by whole-map equality), and no map contains a blank key.
