# Internal Pre-Submission Review 2 — CRM Domain Perspective

**Persona:** Enterprise CRM architect, ~20 years across on-prem CRM suites and two large
replatforming programs (legacy on-prem → cloud CRM); has owned sharing-model redesigns,
currency consolidation, and workflow-engine migrations.
**Reviewed:** 2026-09-01. `legacy_system/` in full (schema, data dictionary, VRL, workflows,
scripts, RBAC matrix, endpoints, batch, audit config), `SYSTEM_OVERVIEW.md`, `DATASET_CARD.md`,
manuscript, and cases RBC-02/RBC-03/INT-01/INT-03/WFL-03/SCR-02/BIZ-02/CFG-03.

**Verdict: The parts that exist ring true; the problem is what does not exist, and one
taxonomy claim in the manuscript outruns the artifact.** As a domain sanity check: yes, I have
lived with systems that look like Meridian CRM 4.2. As a claim of covering "the customization
surfaces of mainstream CRM platforms," no — major surfaces are missing, and the paper should
say which ones.

---

## 1. What is convincingly real

Credit where due — these are exactly the conventions that make legacy CRM migrations bleed:

- **Sentinel dates** (`00000000` = null in `VARCHAR2(8)`, `legacy_schema.sql` comments;
  `SYSTEM_OVERVIEW.md` \S1) and blank-means-default codes (blank `CURR_CD`=USD, blank
  `PREF_CH`=E in `data_dictionary.csv`). Real, common, and used consistently across VRL rules
  (OPP-004), workflows (guards comparing to `'00000000'`), scripts (`DATEDIFF` sentinel rule),
  and export layouts. The lexicographic-compare-with-sentinel-exception rule (\S2) is a
  believable legacy quirk.
- **Soft delete + application-enforced integrity** (no declarative FKs, nightly
  `integrity_check.crms`): textbook early-2000s. A contact pointing at a soft-deleted account
  being an orphan (RIN-01 design in `AUTHORING_GUIDE.md`) is a subtlety migration teams really
  do miss.
- **Denormalized totals** (`ORD_HEADER.TOT_AMT` recomputed nightly by `order_totals.crms`) and
  the invoiced-totals-frozen rule (BIZ-03): plausible.
- **Collect-all validation with BLOCK/WARN severities** (\S2): matches how legacy rule engines
  actually reported errors, and is a real migration hazard (modern frameworks fail-fast).
- **Credit-hold hysteresis** (`credit_hold_sweep.crms`, hold >100% / release ≤80%): the kind of
  undocumented finance-driven band I have found in production scripts. SCR-02's boundary tests
  (exactly at limit; exactly at 80%) test precisely what a naive migration collapses.
- **Fixed-width exports with implied decimals** (`data_dictionary.csv` LAYOUT rows, ANN_REV
  cents zero-padded 15 wide): authentically painful.
- **Vault-reference credentials in INI** (`endpoints.ini`): more disciplined than most real
  legacy shops (which is a realism concession the ethics section rightly makes deliberate).

## 2. What a real CRM has that Meridian lacks (and the paper does not enumerate)

This is my central objection. The following are core customization/config surfaces in every
mainstream CRM of the modeled era and after, and none appears in the benchmark or in the
manuscript's limitation list:

- **Role hierarchy / manager visibility.** `USR_MASTER.MGR_UID` exists in the schema but plays
  no part in the access model (\S5 defines only ALL/TEAM/OWN/NONE flat scopes). Real CRM
  sharing grants managers their reports' records via hierarchy — the single most migration-
  sensitive access construct in practice. **CD-01.**
- **Sharing beyond role scopes:** org-wide defaults, sharing rules, groups/queues, manual
  shares, profile + permission-set layering. The benchmark's one-role-per-user matrix
  (`role_permissions.csv`; `USR_MASTER.ROLE_ID` "assigns exactly one role", \S5) is far simpler
  than any real CRM sharing model, including those of the early 2000s. **CD-01.**
- **Leads and campaigns.** There is a `marketing_sync` integration (INT-03) but no LEAD or
  CAMPAIGN entity anywhere in `legacy_schema.sql` — a CRM with marketing sync but no leads is
  an odd animal; lead conversion mapping is a classic migration horror and is absent. **CD-01.**
- **Multi-currency conversion.** `CURR_CD` is on accounts, opportunities, and orders, and the
  spec says amounts are "in the account's currency" (\S1), but there is no exchange-rate table
  and no conversion semantics; `credit_hold_sweep.crms` sums `TOT_AMT` across orders and
  compares to `CRED_LIMIT` with no currency handling. As modeled, the system is silently
  single-currency with decorative currency codes; SCH-03's minor-units exponent (JPY=0) is the
  only place currency actually bites. Either document the single-currency assumption in
  `SYSTEM_OVERVIEW.md` or add conversion. **CD-05.**
- **Record types, page layouts, UI customization, reports/dashboards.** The taxonomy has no UI
  or reporting category at all; in real replatforming these are a huge fraction of the
  customization inventory. **CD-01/CD-03.**
- **Duplicate/matching rules, approval processes, assignment rules, escalation queues.**
  Approval is reduced to a role check (see \S4 below); dedupe does not exist. **CD-01.**

None of this is fatal for a pilot — but the manuscript claims the twelve categories are
"derived from the customization surfaces of mainstream CRM platforms"
(`LegacyCRM_Bench_OJCS_v1.tex`, \S Taxonomy) with no supporting mapping artifact in
`01_literature/` or anywhere else, and with the above surfaces missing that claim exceeds the
artifact. **CD-03 (Major).** Required: either publish the platform-surface-to-category mapping
that justifies "derived from," or weaken to "twelve categories covering common customization
mechanisms," and enumerate the excluded surfaces (hierarchy/sharing, leads/campaigns,
multi-currency, record types/UI, approvals, dedupe) in \S Limitations item (3).

## 3. Internal consistency problems in the legacy artifact

- **`ORD_HEADER` has no `TEAM_CD` column** (`legacy_schema.sql`), yet the matrix grants
  `MGR,ORD_HEADER,READ,TEAM` and `MGR,ORD_HEADER,UPDATE,TEAM` (`role_permissions.csv`). \S5
  says TEAM compares the user's team to "the record owner's TEAM_CD" — but for orders that
  attribute does not exist on the record, and the spec never says the check resolves the owner
  through USR_MASTER. The RBAC cases dodge this by injecting `record["TEAM_CD"]` "the record
  owner's team" by fiat (`cases/rbac/RBC-02/target_spec.md`, RBC-03 same). A migration team
  working from these artifacts would hit this hole immediately. **CD-02 (Major).** Fix the spec
  (define owner-team resolution) or the schema.
- **`ROLE_PERM` is listed as a table in `SYSTEM_OVERVIEW.md` \S1** ("ROLE_DEF/ROLE_PERM (roles
  and permissions)") **but `legacy_schema.sql` contains no `CREATE TABLE ROLE_PERM`** — the
  permission matrix lives only in `role_permissions.csv`. Spec/schema mismatch in the frozen
  authority document. **CD-06 (Minor).**
- **Comment/code tension inside a normative artifact:** `credit_hold_sweep.crms` comments say
  release "when exposure drops below 80%" while the code is `<=` (at-or-below; SCR-02 tests
  release at exactly 80%). Elsewhere the project treats script comments as normative (SCR-01's
  rounding rule comes from a comment — see `cases/legacy_scripts/SCR-01/GROUND_TRUTH.md`
  line 5). If comments carry semantics, they must be exact. **CD-09 (Editorial).**

## 4. Preservation of business logic

The logic that is modeled is preserved with care — the VRL evaluation-order and collect-all
semantics, the OLD.-value transition rules (ACC-004 credit-hold release, OPP-005 no reopening
won), and the invoiced-order cancellation path (E5003 + `ORD_CANC_INV` + credit note in
WFL-03/BIZ-03) are the right hazards and are tested from both the rules side and the workflow
side, which is exactly how a migration misses them.

One rule is domain-wrong, though: **ORD-002 checks the *order owner's* role, not the acting
user's** (`validation_rules.vrl`: `LOOKUP(USR_MASTER, USR_ID, OWNER_UID, ROLE_ID)`). As
written, any clerk editing an order owned by a manager gets manager discount authority, and a
manager's own orders can carry any discount regardless of who edits them. Real discount
governance binds to the actor (or an approval chain). BIZ-02's target spec papers over this by
defining "the acting user (the order's owner performing the update)"
(`cases/business_rules/BIZ-02/target_spec.md`) — i.e., it declares actor==owner rather than
fixing the model. VRL simply has no current-user concept (\S2 grammar), which is the real
cause. Acceptable as a documented legacy quirk, but it should be flagged as such in
`SYSTEM_OVERVIEW.md`, not silently normalized. **CD-04 (Minor).**

## 5. Workflow complexity vs. real CRM workflows

Three workflows, 6–9 transitions each, single-event `fire()`, actions limited to set/audit/
notify, day-granularity timers evaluated by nightly batch (\S3). For an early-2000s system the
*shape* is right (I have migrated engines exactly like this), but real CRM workflow migrations
break on: cascading field updates re-triggering rules, cross-object actions, queue-based
time-dependent actions with clock skew, and recursion limits. None is modeled; WFL tests never
chain two events (see SE review \S2). Fine for a pilot — but \S Practical Implications'
"checklist of migration hazards" framing should not imply workflow coverage beyond
first-match/guard/order semantics. **CD-07 (Minor).**

## 6. Access control model vs. real CRM sharing

Covered above (CD-01/CD-02). What the model does get right: deny-by-default with explicit
grants, the ADMIN row-must-exist subtlety (RBC-02 — this is a genuinely good test of a real
migration failure mode, over-widening admin), the AUDIT read-only role, and asymmetric grants
(MGR READ ALL on accounts but TEAM on opportunities, `role_permissions.csv`) which RBC-03's
720-tuple enumeration does exercise. The EXPORT action existing only for ACCT_MASTER — so no
role can export contacts — is a nice deny-by-default touch for the PII-heavy entity.

## 7. Integration scenarios

The four endpoints (`endpoints.ini`) are a plausible minimal set (ERP push, DW load, notifier,
marketing sync), and fixed-width/CSV/XML payload variety is right for the era. Missing, and
worth one limitation sentence: inbound integrations (everything here is outbound), message
ordering/idempotency semantics, and any error-payload contract for the notifier. INT-02's
77-char record with implied-decimal cents is the most realistic single artifact in the set.

## 8. Practical usefulness to a migration team

Honest answer: as a *benchmark* for tooling evaluation, plausible; as practitioner material,
the per-case `GROUND_TRUTH.md` derivations and the convention checklist (C2 prompt) are the
transferable assets. A migration team gets no vendor-metadata ingestion, no data-volume
dimension (716 rows), and no dirty-data cases — every flag is a clean 'Y'/'N'/blank, every
date is well-formed or exactly `00000000` (see fixtures across all sampled tests). Real legacy
data has lowercase flags, `19000101` pseudo-nulls, and truncated encodings; a "dirty data"
category would raise practical value materially. **CD-08 (Minor).**

## 9. Manuscript claims vs. enterprise realism (the hunt requested)

- \S Taxonomy "derived from the customization surfaces of mainstream CRM platforms" — exceeds
  the artifact (CD-03, above). This is the one claim I would fight in external review.
- Abstract/Intro "enterprise CRM customizations" — borderline; defensible because \S Threats
  and Limitations (3) bound it, but the title carries no such bound.
- \S Practical Implications "the case format doubles as a checklist of migration hazards" —
  true only for the modeled hazard subset; with CD-01's missing list, a team using it as *the*
  checklist would be exposed. Soften or enumerate exclusions.
- \S1 "the risk is concentrated in this layer" — matches my experience, but it is an empirical
  assertion with no citation; either cite industry postmortem literature or mark as motivation.
  (Logged as AD-13 in the adversarial review.)
- Everything quantitative I checked matches the artifacts; no realism claim is propped up by a
  wrong number.

## Issue summary (this review)

| ID | Severity | Location | Issue |
|---|---|---|---|
| CD-01 | Major | legacy_schema.sql; SYSTEM_OVERVIEW.md \S5; taxonomy | Missing core CRM surfaces: role hierarchy (MGR_UID unused), sharing rules/permission sets, leads/campaigns, record types/UI, approvals, dedupe |
| CD-02 | Major | legacy_schema.sql ORD_HEADER vs role_permissions.csv | TEAM-scope grants on an entity with no TEAM_CD; owner-team resolution undefined; cases inject the value by fiat |
| CD-03 | Major | tex \S Taxonomy | "Derived from the customization surfaces of mainstream CRM platforms" unsupported by any mapping artifact; overreach |
| CD-04 | Minor | validation_rules.vrl ORD-002; BIZ-02 target_spec.md | Discount governance binds to record owner, not actor; BIZ-02 normalizes rather than flags the quirk |
| CD-05 | Minor | SYSTEM_OVERVIEW.md \S1; credit_hold_sweep.crms | Multi-currency codes present but no conversion semantics; exposure math silently single-currency |
| CD-06 | Minor | SYSTEM_OVERVIEW.md \S1 vs legacy_schema.sql | ROLE_PERM table referenced in spec, absent from schema |
| CD-07 | Minor | workflows.xml; WFL cases | Workflow complexity well below real CRM engines; no multi-step trajectories |
| CD-08 | Minor | all case fixtures; seed_data/ | No dirty-data dimension; all legacy values clean; low volume (716 rows) |
| CD-09 | Editorial | credit_hold_sweep.crms comment; SCR-01 GROUND_TRUTH.md | Normative-comment imprecision ("below 80%" vs `<=`); comments elsewhere carry load-bearing semantics |
