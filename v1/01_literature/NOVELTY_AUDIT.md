# Novelty Audit — LegacyCRM-Bench

Audit date: 2026-09-01. Basis: 38 primary-source-verified references
(`REFERENCE_VERIFICATION.csv`), detailed comparisons in `PRIOR_WORK_NOTES.md`, structured
comparison in `prior_work_matrix.csv` / `PRIOR_WORK_MATRIX.xlsx`, queries in `SEARCH_LOG.md`.

## Claims LegacyCRM-Bench must NOT make

1. **Not the first CRM benchmark.** CRMArena (NAACL 2025) and CRMArena-Pro (arXiv:2505.18878)
   are established CRM agent benchmarks with realistic Salesforce-style synthetic orgs;
   WorkBench includes CRM-like data; WorkArena runs on live ServiceNow.
2. **Not the first enterprise benchmark with access controls.** EnterpriseBench (EMNLP 2025)
   models access-control hierarchies; CRMArena-Pro probes confidentiality awareness.
3. **Not the first execution-based code-translation evaluation.** TransCoder (2020),
   CodeTransOcean (2023), Pan et al. ICSE 2024, and AlphaTrans (FSE 2025) all evaluate
   translation with executable oracles; AlphaTrans already does repository-level
   differential validation during migration.
4. **Not the first migration benchmark.** PyMigBench (MSR 2023) benchmarks real Python
   library migrations; the ASE 2025 follow-up evaluates LLMs on them.
5. **Not the first legacy-modernization equivalence-testing work.** IBM's 2025 COBOL-to-Java
   line does industrial equivalence validation of modernized code.

## The defensible distinction (and its honest boundaries)

LegacyCRM-Bench evaluates a question none of the above operationalizes: **when an LLM-assisted
process migrates the *customization layer* of a legacy CRM (schema mappings with sentinel
conventions, declarative validation rules, workflow state machines, procedural legacy scripts,
role-based access-control matrices, integration configurations and payload layouts, batch-job
semantics, audit-logging behavior, referential-integrity conventions), does the migrated
implementation preserve the documented legacy behavior — including its security semantics?**

Specifically novel elements, each scoped:
- **Object of evaluation**: the customization artifacts themselves under transformation —
  not agent task execution inside a fixed org (CRMArena line, EnterpriseBench, WorkBench,
  WorkArena), and not function-level language translation (TransCoder/Pan et al.).
- **Preservation-oriented oracles**: executable acceptance tests per case that encode
  *behavioral fidelity to a documented legacy semantics*, including deny-by-default RBAC
  equivalence, audit append-only/per-column granularity, privacy exclusions (opt-out),
  hallucination checks (no invented states/codes/permissions). Prior migration validation
  (AlphaTrans, IBM line) checks I/O equivalence of translated code but not
  platform-customization properties such as RBAC widening or audit fidelity.
- **Fully open, deterministic, offline harness** with synthetic-but-documented legacy
  semantics — addressing the reproducibility gap of the industrial modernization line and the
  contamination worries of organic-provenance benchmarks (SWE-bench audits, LiveCodeBench).

Honest boundaries to state in the paper:
- The legacy system is **synthetic and simplified**; enterprise realism is bounded (a fictional
  documented DSL, not a real vendor's metadata format). Claims about real-world Salesforce/
  Dynamics/etc. migrations must not be made.
- The pilot scale (36 cases) supports feasibility and instrument-validity claims, not broad
  model rankings; scale-up is future work.
- Framing must be "migration-fidelity benchmark for CRM customizations", never "first CRM
  benchmark", "first migration benchmark", or "production-validated".

## Naming-collision check

Web searches on 2026-09-01 (see SEARCH_LOG.md) found no existing benchmark named
"LegacyCRM-Bench". Closest names: CRMArena(-Pro), EnterpriseBench, PyMigBench. The name is
usable; the Related Work section must nonetheless disambiguate from the CRMArena line
prominently (first paragraph).
