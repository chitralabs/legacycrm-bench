# Internal Pre-Submission Review 3 — Security & Privacy Perspective

**Persona:** Security and privacy reviewer; background in evaluation-infrastructure security,
authorization-model verification, and running untrusted-code benchmarks.
**Reviewed:** 2026-09-01. Harness (`03_source_code/harness/*`), study protocol and experiment
plan (`04_experiments/`), C4 prompt template, RBAC artifacts and cases RBC-02/RBC-03, INT-01/
INT-03, WFL-03, SCR-02; manuscript ethics/threats sections; DATASET_CARD.md.

**Verdict: The benchmark's security *oracles* are above the bar for this literature; the
benchmark's own *execution security posture* is not.** The single most important finding is
that the planned evaluation will execute model-generated Python with no isolation whatsoever.
That must be fixed in the protocol before the first C1 run, and the paper should say how.

---

## 1. Cross-tenant leakage and tenancy scope

Meridian CRM 4.2 is a single-organization system: one schema, one user table, one permission
matrix; there is no tenant concept anywhere in `legacy_schema.sql` or `SYSTEM_OVERVIEW.md`.
That is a legitimate design choice for an on-prem-era artifact — but it means an entire class
of modern-CRM security risk (cross-tenant/cross-org isolation, the confidentiality dimension
CRMArena-Pro explicitly probes, which the paper itself cites in \S2.1) is out of scope, and
**nothing in the manuscript or `DATASET_CARD.md` discloses the single-tenant scope.** The
abstract and conclusion sell "security semantics included" without stating that the security
surface is intra-org RBAC + privacy exclusions + audit only. **SP-03 (Major).** Required: one
sentence in \S Threats or \S Limitations scoping the security claims to single-tenant,
intra-organizational semantics, and noting multi-tenant isolation as out of scope.

## 2. Authorization-preservation oracles (RBC-03 and friends)

I attempted to break the RBC-03 equivalence oracle and largely failed, which is to the
project's credit:

- The 720-tuple space (6 users incl. an unknown role × 4 records incl. soft-deleted × 6
  objects × 5 actions, `cases/rbac/RBC-03/tests/test_acceptance.py`) is computed against a
  hand-written `legacy_can()` transcribed from \S5/\S1 prose, with a separate
  widening-direction test (`test_no_privilege_widening_anywhere`) — the right asymmetric
  framing for security.
- The matrix asymmetries are genuinely exercised: MGR READ ALL on ACCT_MASTER vs. TEAM on
  OPP_MASTER falls inside the enumeration; ADMIN-without-row denial (EXPORT on OPP_MASTER) and
  ADMIN-DELETE-on-soft-deleted denial have dedicated tests; EXPORT exists only for ACCT_MASTER
  in `role_permissions.csv`, so contact export is deny-by-default for every role and the
  enumeration confirms it. The policy-scan tests (no grant absent from the matrix, no scope
  change, exact file order) close the config-hallucination channel.

Residual gaps, all real but bounded — **SP-05 (Minor):**

1. **`NONE` scope is never exercised in RBC-03's decision space** because
   `role_permissions.csv` contains zero NONE rows (grep confirms). A `policy.json`/`can()`
   pair that mapped NONE→allow would pass RBC-03 entirely. RBC-01 does test `can()`'s NONE
   branch with a synthetic row (`cases/rbac/RBC-01/tests/test_acceptance.py` line ~63), so the
   category is not blind — but RBC-03, the case that claims full-matrix equivalence, should add
   a synthetic NONE grant to its enumeration or to a dedicated test.
2. **Blank-identity equality is untested.** Both `legacy_can()` and the reference treat
   `"" == ""` as a match for TEAM (and OWN) scope; no fixture has a blank `TEAM_CD` or blank
   `OWNER_UID`. A record with an empty owner-team matched by a user with an empty team is a
   classic widening bug in real migrations, and here the *documented* semantics arguably permit
   it (\S5 says only "must equal"). The spec should state the blank-identity rule and the tests
   should pin it.
3. The RBC target specs must inject `record["TEAM_CD"]` as "the record owner's team" because
   the spec never defines owner-team resolution and ORD_HEADER lacks the column (see
   CRM-domain review CD-02) — the oracles inherit that underdefinition.
4. Internal validity: the equivalence oracle, the semantics prose, and the reference share
   authorship and repository. Disclosed in \S Threats ("Internal"), and the null/mutation
   evidence mitigates. RBC-03's one surviving mutant (`surviving_mutants.csv`: RBC-03
   CBR:bool, node 169 — the flipped `delete_requires_live_record` default masked by
   policy.json) has been classified EQUIVALENT by the parallel triage completed during this
   audit (`09_peer_review_audit/mutant_triage.md`, entry 14). More important for this review:
   that triage *confirms* TEST_GAP survivors in RBC-01 (no ADMIN user ever exercised; blank
   DEL_FLG on DELETE untested) and RBC-02 (no granting OWN row exercised) — authorization
   oracle gaps that must be fixed before release (tracked as SE-04).

## 3. Credential handling

Design-level: excellent. Secrets exist only as `vault://` references (`endpoints.ini`), the
INT-01 target schema forces `secret_ref` to remain a reference, and
`test_secret_refs_remain_vault_references` plus `test_no_literal_credential_material_in_deliverable`
encode "no credential literals" as an executable expectation. Seed data contains no secrets.

Enforcement-level: the scans are heuristics and should be labeled as such — **SP-04 (Major)**:

- INT-01's token regex `[A-Za-z0-9+]{24,}` (`cases/integration/INT-01/tests/test_acceptance.py`)
  misses base64url alphabets (`-`, `_`), hex tokens under 24 chars, and dotted/segmented
  secrets (JWT-style `a.b.c` never matches because `.` breaks the run); keyword list
  (`password`, `passwd`, `bearer `, `authorization`) misses `secret`, `token`, `api_key`,
  `x-api-key`.
- The forbidden-import checks in tests (`"requests" not in src` etc., e.g. RBC-02/RBC-03/
  WFL-03/SCR-02 final tests) and in `validate_cases.py` (`FORBIDDEN` regex) are substring/
  regex matches that miss `os.system`, `ftplib`, `smtplib`, `ctypes`, `__import__("socket")`,
  and string-assembled imports. Against the authors' own references this is fine; against
  model-generated or adversarial candidates — the population these security oracles will
  actually judge under C1–C4 — they are trivially evadable, and a "security-violation count"
  metric (`STUDY_PROTOCOL.md` \S5) built on them will undercount.
- Required: state in \S Oracles that credential/import scans are heuristic tripwires, not
  enforcement; move real enforcement to the execution environment (below); optionally add an
  AST-based import check to replace the substring scans.

## 4. The arbitrary-code-execution problem (headline finding)

`03_source_code/harness/run_case.py` executes candidate deliverables by importing them inside
a pytest subprocess:

- `env = dict(os.environ)` — the candidate inherits the **full user environment**. During
  future model runs, the runner will hold provider API keys in that environment
  (`ESTIMATED_COSTS.md` authorization checklist: "credentials are supplied via
  environment/keychain"); as designed, every model-generated solution would be able to read
  them.
- No network isolation (G4 "no network" in the manuscript is a property *asserted of the
  benchmark's own code*, not enforced on candidates), no filesystem sandbox (candidate code
  runs with the invoking user's privileges: `~/.ssh`, the whole repo, and the raw-output
  store are readable/writable), no memory/CPU rlimits — only a 600 s wall timeout.
- Neither `STUDY_PROTOCOL.md` nor `EXPERIMENT_PLAN.md` ("Runner design") mentions sandboxing,
  containers, or privilege separation at all.

For the executed instrument validation (running the project's own references and mutants of
them) the realized risk is negligible. But the paper's entire purpose is that this harness
will execute **untrusted LLM output** under C1–C4. Model-generated code executing with user
privileges, inherited API keys, and open network is an arbitrary-code-execution-by-design
pipeline. **SP-01 (Critical).** Required before any model run, and worth a paragraph in the
manuscript (\S Setup or \S Ethics): execute candidates in a disposable container/VM or at
minimum an unprivileged user + network-denied namespace; pass a scrubbed environment
(whitelist `LCB_SOLUTION_DIR`, `PYTHONHASHSEED`, `PYTHONPATH` only); apply rlimits (CPU,
memory, file size, process count); mount the case directory read-only; treat candidate output
files as data (never import into the runner process itself).

## 5. Oracle leakage at runtime (gaming vector)

Related but distinct: candidate code executes *inside the test process tree, next to the
oracle*. A candidate module can walk the stack at import time (`inspect`/`traceback`), recover
the test file's path, and read `tests/test_acceptance.py`, `GROUND_TRUTH.md`, or
`reference/migrated.py` from the case directory — then answer accordingly. Nothing in
`run_case.py` prevents, detects, or logs this. The C4 design carefully redacts assertion
values from *prompts* (`04_experiments/prompts/C4_repair_loop.md`), but a repair-capable model
can simply emit code that reads the un-redacted oracle from disk at test time; the
contamination controls (`STUDY_PROTOCOL.md` \S7 "Acceptance tests are never included in
prompts") do not cover the runtime channel. **SP-02 (Major).** Required: run candidates
against a sanitized copy of the case (tests only, no `reference/`, no `GROUND_TRUTH.md`), or
enforce file-access restriction in the sandbox of SP-01, and add a runner check that flags
candidates reading outside their solution directory. This also deserves a sentence in \S
Threats — it is currently an undisclosed validity threat to every future C4 number.

Note also that the C4 redaction mechanism itself (`runner/redact_failures.py`) does not exist
yet — `03_source_code/runner/` is absent — and its leakage audit is a 10% manual sample per
run (`C4_repair_loop.md`), which can demonstrate presence but never absence of leakage. The
manuscript's Limitations (6) admits this honestly; keep that sentence. **SP-06 (Minor).**

## 6. Privacy

- The opt-out oracles are the strongest privacy tests I have seen in a code benchmark:
  INT-03 asserts the *absence* of every field of an excluded contact (id, email, first/last
  name) from the payload, covers blank-flag-means-included, and the reference implements
  exclusion before any serialization (`cases/integration/INT-03/`). Good.
- Scope caveat: opt-out preservation is tested on exactly one outbound channel
  (marketing_sync). SCH-02 maps `OPTOUT_FLG` to a modern boolean, but no case tests that a
  *combination* migration (schema + integration) keeps the exclusion; and the manuscript's
  "privacy exclusions" phrasing (\S Oracles, \S Implications) reads broader than one channel.
  **SP-07 (Minor).**
- Append-only audit with per-column OLD_VAL/NEW_VAL (`SYSTEM_OVERVIEW.md` \S8, AUD-03) will
  persist personal data indefinitely by design; the tension between append-only audit and
  data-subject erasure (soft-delete vs. audit trail) is a real migration hazard the ethics
  section (\S Ethics) never mentions. Synthetic data makes this harmless here, but as
  "checklist of migration hazards" material it is a notable omission. **SP-07.**
- Seed data is fictional by construction (`generate_seed_data.py`, word lists; ledger C014).
  No issue.

## 7. Threat-model completeness

There is no consolidated threat model. Individual threats are handled where the authors
thought of them (contamination in `STUDY_PROTOCOL.md` \S7; oracle leakage in C4 redaction;
credential hygiene in INT-01), but nothing covers: malicious/gaming candidates (SP-02),
harness compromise via candidate execution (SP-01), evaluation-infrastructure secrets (SP-01),
or misuse of the benchmark as a jailbreak vehicle (low risk, but one line). **SP-08 (Minor).**
Required: a short threat-model subsection (assets: oracle integrity, host, API keys, result
integrity; adversaries: gaming model output, contaminated training, malicious PR to the public
repo) in the manuscript or `DATASET_CARD.md`.

## Issue summary (this review)

| ID | Severity | Location | Issue |
|---|---|---|---|
| SP-01 | Critical | harness/run_case.py; STUDY_PROTOCOL.md \S3; EXPERIMENT_PLAN.md runner design | Future model runs execute untrusted generated code with inherited env (API keys), no sandbox, no network/filesystem/resource isolation |
| SP-02 | Major | harness/run_case.py; STUDY_PROTOCOL.md \S7 | Candidates execute beside the oracle and can read tests/GROUND_TRUTH/reference at runtime; C4 redaction does not cover this channel |
| SP-03 | Major | tex abstract/conclusion; DATASET_CARD.md | Single-tenant scope of all security claims undisclosed; cross-tenant isolation silently out of scope |
| SP-04 | Major | INT-01 tests; validate_cases.py FORBIDDEN; RBC/WFL/SCR scan tests | Credential and import scans are evadable heuristics; security-violation metric will undercount on adversarial candidates |
| SP-05 | Minor | cases/rbac/RBC-03 tests; role_permissions.csv | NONE scope absent from RBC-03's 720-tuple space; blank TEAM_CD/OWNER_UID equality untested; owner-team resolution underdefined |
| SP-06 | Minor | 04_experiments/prompts/C4_repair_loop.md; 03_source_code/runner (absent) | Redaction script unimplemented; 10% sampled leakage audit cannot show absence |
| SP-07 | Minor | INT-03; tex \S Oracles/\S Ethics | Privacy oracle covers one channel; append-only audit vs. erasure tension unaddressed |
| SP-08 | Minor | project-wide | No consolidated threat model for the benchmark or its evaluation pipeline |
