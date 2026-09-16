# Human-Verification Integrity Audit (Phase 3) — Determination

Audit date: 2026-09-16. Scope: every artifact touching submission-readiness item B7 —
the ground-truth spot-check notes, the verification record, the signed page, and every
place their outcome is described (audit archive, ledger, readiness documents, public
repository).

## Documentary chain (what the records actually establish)

1. **Derivation notes** (supplied by the author 2026-09-15; archived in
   `v1/09_peer_review_audit/GROUND_TRUTH_SPOTCHECK.md`): self-described as an
   **AI-assisted** independent reasoning pass over five cases (SCH-01, SCR-01, RBC-01,
   WFL-01, INT-02), derived from target specifications and legacy artifacts with tests and
   reference implementations excluded. The notes themselves state they are "not a human
   colleague's verification."
2. **Archive-time mechanical re-verification** (this project, 2026-09-15): all cited legacy
   files exist; the five headline expected values match the recorded `GROUND_TRUTH.md`
   entries. This is machine/AI verification, not human verification.
3. **Verification record** (`B7_verification_record.docx`, unsigned): a structured record
   naming reviewer an external third-party reviewer, containing the same five derivations, with all
   five reviewer-decision boxes already marked "Confirmed" and the header
   "CASE DECISIONS COMPLETED — SIGNATURE PENDING."
4. **Signed page** (`B7_attestation_signed.pdf`): one page — affiliation (an industry firm),
   email, date (September 15, 2026), and a handwritten signature.

## Determination

The records establish that an external third-party reviewer **reviewed and signed** a verification
record whose derivations and "Confirmed" decisions trace back to an AI-assisted analysis.
The records do **not** establish that he personally re-derived the expected values from the
legacy artifacts and specifications: no work product of his own derivation exists in the
archive, and the decision boxes were marked complete in the unsigned record before
signature, with no documentation of who marked them.

Accordingly, describing this as "independent human verification" or stating that the signer
"re-derived" the cases **overstates the documented evidence** and has been corrected
everywhere it appeared (it never appeared in the manuscript, which claims only that ground
truth was "spot-audited during internal review" — accurate).

## Approved wording (used everywhere from v4 onward)

> "Human review and signed attestation (an external third-party reviewer, 2026-09-15) of an AI-assisted
> preliminary ground-truth spot-check covering five cases, whose derivations were produced
> from specifications and legacy artifacts with tests and references excluded, and whose
> concordance with the recorded ground truth was mechanically re-verified at archive time."

## Corrections applied (v1 evidence archive + public repository; v3 left untouched)

- `GROUND_TRUTH_SPOTCHECK.md` attestation block: "re-derived each of the five cases'
  expected values" (attributed to the signer) → replaced with the approved wording.
- Claim ledger C034: "verified and SIGNED by an independent human reviewer" → "reviewed and
  signed"; claim retitled to match the approved wording.
- Readiness report / blockers B7 rows: "Independent human verification … re-derived 5 cases
  specs-only" → approved wording; B7 reclassified from CLOSED to
  **CONDITIONALLY CLOSED (wording corrected) — upgrade path available**.
- Public repository copies of the above: corrected in the same commit as this audit.
- The signed page and record are unaltered and remain in the **private** archive only
  (personal signature and email are not published).

## Upgrade path (optional, not prefilled)

If Mr. [reviewer] in fact personally re-derived the five cases, the stronger claim can be
restored upon receipt of either (a) his own derivation notes/worksheets, or (b) a short
written statement from him explicitly confirming personal re-derivation without consulting
tests or references. A clean re-verification protocol he could genuinely complete from
scratch is described in `B7_verification_record.docx`'s method section; if used, he must
mark the decisions himself. **Nothing is prefilled on his behalf in v4.**

## Effect on submission readiness

The manuscript requires no change (it never made the claim). The audit trail is now
truthful. B7's substance — spec-only derivation concordance, mechanically re-verified,
human-reviewed and signed — stands; only the characterization changed. This item is not a
submission blocker under the corrected wording, but the author should read this audit and
confirm the characterization before submitting (listed in the confirmation checklist).
