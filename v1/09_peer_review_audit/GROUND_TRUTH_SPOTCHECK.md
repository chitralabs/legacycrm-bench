# Ground-Truth Spot-Check (B7) — Archive

**Provenance:** The notes below were supplied by the author on 2026-09-15. They are an
AI-assisted independent derivation pass over five cases (one per behavioral family),
performed from target specifications and legacy artifacts only, with tests and reference
implementations excluded during derivation. The notes state their own limitation: they are
not, by themselves, a human colleague's verification.

**Archive-time verification (2026-09-15, this project):** all cited legacy source files
exist at the cited paths, and the five headline concordance claims were re-checked against
the corresponding `GROUND_TRUTH.md` records (blank-numeric→0.0 in SCH-01; the 5.005→5.01
half-up boundary in SCR-01; the DELETE soft-deletable rule in RBC-01; literal-string
`<set>` values in WFL-01; the 77-character layout and half-up cents conversion in INT-02).
All matched.

**Status of B7:** CONDITIONALLY CLOSED (wording corrected 2026-09-16): human-reviewed-and-signed AI-assisted spot-check; personal re-derivation by the signer is not documented and is not claimed. Previously PARTIALLY satisfied — the derivation-independence property holds
(specs-only derivation, 5/5 concordant), but the human attestation below must be completed
to close the item. Until then the manuscript's Threats statement ("spot-audited") remains
the operative claim.

---

## Supplied notes (verbatim)

# Ground Truth Spot Check Notes for Human Review

## Purpose and status

These notes document an AI-assisted, independent reasoning pass over five LegacyCRM-Bench cases. The calculations were performed from the case target specifications and legacy artifacts. Acceptance tests and reference implementations were not opened or executed during the derivation.

After the expected values had been derived, they were compared with the corresponding `GROUND_TRUTH.md` records. All five comparisons were concordant. This work is useful as a preliminary audit, but it is not a human colleague's verification and does not by itself close submission-readiness item B7. A human reviewer should check the source files, confirm or amend the notes, and complete the attestation at the end.

## Materials and method

Authoritative archive: `../v1/02_benchmark_dataset/`

For each selected case, the following were used during derivation: `target_spec.md`; files under the case's `legacy/` directory; `case.json` only for case identification and scope. Deliberately excluded during derivation: `tests/test_acceptance.py`; all files under `reference/`; harness output and model output. Only after each calculation was written down was the corresponding `GROUND_TRUTH.md` opened for comparison.

## Summary

| Case | Category | Main property checked | Result |
|---|---|---|---|
| SCH-01 | Schema mapping | Sentinel, default, type, and key conversions | Concordant |
| SCR-01 | Legacy script | Decimal arithmetic, half-up rounding, deletion filtering, audit condition | Concordant |
| RBC-01 | Access control | TEAM, OWN, ALL, missing-row, and DELETE semantics | Concordant |
| WFL-01 | Workflow | Guard evaluation, state transition, ordered actions, no-match behavior | Concordant |
| INT-02 | Integration | Fixed-width offsets, padding, defaults, half-up cents conversion | Concordant |

Overall result: **5 of 5 cases concordant; 0 discrepancies identified.**

## Case 1 SCH-01 Account schema mapping

Input vector: ACCT_ID=A00000123, ACCT_NM=Northwind Services, ACCT_TYP=C, SIC_CD=7372, REGION_CD=NAM, ANN_REV=125000.50, CURR_CD blank, OWNER_UID=U0000001, TEAM_CD=T001, CRED_LIMIT blank, CRED_HOLD blank, CREATE_DT=20260131, UPD_DT=00000000, DEL_FLG=N.

Derivation: ANN_REV numeric -> 125000.5; blank CURR_CD -> USD; blank CRED_LIMIT -> 0.0 (empty-numeric-is-zero); blank CRED_HOLD means N -> credit_hold False; 20260131 -> 2026-01-31; 00000000 sentinel -> None; DEL_FLG not an output field (Y would exclude the row, returning None). Expected output: the 13 modern keys exactly (account_id A00000123, name Northwind Services, account_type C, sic_code 7372, region NAM, annual_revenue 125000.5, currency USD, owner_id U0000001, team_code T001, credit_limit 0.0, credit_hold False, created_date 2026-01-31, updated_date None) and no legacy key names. Comparison with SCH-01/GROUND_TRUTH.md: concordant.

## Case 2 SCR-01 Order total recomputation

Input: order O00000001 (live, STAT_CD=N, DISC_PCT=15, incoming TOT_AMT=0); line 1 QTY=3 UNIT_PRC=19.99 EXT_AMT=0 live; line 2 QTY=5 UNIT_PRC=100 EXT_AMT=500 soft-deleted.

Derivation: line 1 -> 3 x 19.99 = 59.97; line 2 excluded, stored EXT_AMT=500 unchanged; total 59.97; 15% discount -> 59.97 x 0.85 = 50.9745 -> half-up to cents 50.97; incoming 0 differs -> audit (ORD_RETOTAL, O00000001); returned objects are copies. Boundary cross-check: 1 x 10.01 at 50% -> 5.005 -> half-up 5.01, not 5.00. Comparison with SCR-01/GROUND_TRUTH.md: concordant.

## Case 3 RBC-01 Permission decisions

User U0000003, ROLE_ID=REP, TEAM_CD=T01. Decisions derived: READ ACCT_MASTER same-team foreign owner -> True (REP/READ/TEAM); READ ACCT_MASTER team T02 -> False; UPDATE OPP_MASTER own record -> True (OWN); UPDATE OPP_MASTER other user same team -> False (OWN checks user id); DELETE OPP_MASTER own -> False (no REP DELETE row); ADMIN READ ACCT_MASTER foreign -> True (row exists, scope treated as ALL); ADMIN DELETE ACCT_MASTER with DEL_FLG=Y -> False (DELETE requires live record). Unknown role or empty matrix -> False (missing rows mean NONE). Comparison with RBC-01/GROUND_TRUTH.md: concordant.

## Case 4 WFL-01 Opportunity workflow

Transitions derived: P+qualify with AMT=1500 -> Q, STAGE_PCT "25", audits [OPP_QUAL], matched True; P+qualify with blank AMT (blank->0, guard false) -> stays P, audits [WF_NOMATCH], matched False; Q+advance (no guard) -> N, STAGE_PCT "60"; N+close_won with CLOSE_DT=20260915 -> W, STAGE_PCT "100", audits [OPP_WON], notifications [won_deal]; N+close_won with CLOSE_DT=00000000 (guard false) -> stays N, [WF_NOMATCH]. Set values remain strings (XML literals); actions apply in document order only on successful transitions. Comparison with WFL-01/GROUND_TRUTH.md: concordant.

## Case 5 INT-02 Fixed-width account export

Input: ACCT_ID=A123, ACCT_NM=Acme, REGION_CD=NAM, ANN_REV=999.995, CRED_HOLD blank, CREATE_DT blank. Layout widths 10+40+3+15+1+8 = 77. Segments: [A123 + 6 spaces][Acme + 36 spaces][NAM][000000000100000 (999.995 x 100 = 99999.5 -> half-up 100000, zero-padded 15)][N (blank default)][00000000 (blank date)]. Exactly 77 characters, no terminator. Comparison with INT-02/GROUND_TRUTH.md: concordant.

## Preliminary conclusion

Across five cases from five distinct behavioral categories, the expected values recorded in the benchmark were reproducible from the documented legacy semantics and case specifications without consulting the tests or reference implementations. The sample supports the internal consistency of the selected ground-truth records. It does not establish correctness for the other 31 cases and does not substitute for an independent human audit.

---

## Human attestation (required to close B7)

COMPLETED 2026-09-15 as **human review and signed attestation** of this AI-assisted
spot-check (wording corrected 2026-09-16 by the Phase-3 integrity audit; see
v4/HUMAN_VERIFICATION_INTEGRITY_AUDIT.md):

- Reviewer of record: **an external third-party reviewer** — third party (an industry firm), not an
  author of this work.
- What the records establish: he reviewed and signed a verification record containing the
  five AI-assisted derivations, with all five decisions marked Confirmed and no amendments.
  The records do NOT document a personal re-derivation by the signer; the derivations
  themselves were produced with tests/references excluded and were mechanically re-verified
  against the recorded ground truth at archive time.
- Date: September 15, 2026. Signature: on file in the private archive
  (`B7_attestation_signed.pdf`; full record `B7_verification_record.docx`/`.txt`).
