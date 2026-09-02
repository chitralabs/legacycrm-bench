# Search & Verification Log — LegacyCRM-Bench prior-work audit

All queries and API calls executed on **2026-09-01**.

## Verification policy
- Every reference in REFERENCE_VERIFICATION.csv was verified against a primary source on 2026-09-01: the arXiv API (export.arxiv.org — returns title/authors/dates straight from the arXiv record), an arXiv abstract page fetch, the Crossref works API (api.crossref.org), or an ACL Anthology page fetch.
- Anything that could not be verified against a primary source was marked UNVERIFIED and excluded from the CSV (see bottom).

## Web searches (search engine)
1. `EnterpriseBench benchmark enterprise LLM agents arXiv` — located EnterpriseBench candidate (arXiv:2510.27287) and adjacent enterprise-agent benchmarks.
2. `LLM COBOL modernization benchmark arXiv COBOL to Java translation evaluation` — located IBM COBOL-to-Java testing/validation/quality papers (arXiv:2504.10548, 2506.10999, 2507.23356).
3. `CRMArena Huang aclanthology NAACL 2025` — located ACL Anthology record 2025.naacl-long.194 for CRMArena venue/pages verification.

## arXiv API batch verifications (https://export.arxiv.org/api/query?id_list=...)
Batch 1 (28 IDs, all returned with matching titles/authors):
2411.02305 (CRMArena), 2505.18878 (CRMArena-Pro), 2405.00823 (WorkBench), 2406.12045 (tau-bench), 2403.07718 (WorkArena), 2308.03688 (AgentBench), 2006.03511 (TransCoder), 2308.03109 (Lost in Translation), 2310.04951 (CodeTransOcean), 2107.03374 (HumanEval), 2108.07732 (MBPP), 2310.06770 (SWE-bench), 2305.01210 (EvalPlus), 2108.09293 (Asleep at the Keyboard), 2312.04724 (CyberSecEval), 2404.13161 (CyberSecEval 2), 2411.00640 (Adding Error Bars to Evals), 2308.08493 (Time Travel in LLMs), 2310.18018 (NLP Evaluation in trouble), 2403.07974 (LiveCodeBench), 2306.03091 (RepoBench), 2102.04664 (CodeXGLUE), 2406.15877 (BigCodeBench), 2401.13178 (AgentBoard), 2410.24117 (AlphaTrans), 2405.11514 (Translating to Rust), 2507.02825 (Rigorous Agentic Benchmarks), 2411.14971 (Legacy Code Modernization/MITRE).

Batch 2 (4 IDs): 2507.23356, 2504.10548, 2506.10999 (COBOL line), 2510.27287 (EnterpriseBench).

## arXiv abstract page fetch
- https://arxiv.org/abs/2510.27287 — confirmed title, authors (Vishwakarma et al.), and "Accepted at EMNLP 2025 Main Track" comment; confirms the paper introduces EnterpriseBench.

## Crossref API record fetches (https://api.crossref.org/works/{DOI})
- 10.1145/1993498.1993532 — Csmith (Yang et al., PLDI 2011, pp. 283-294)
- 10.1214/aos/1176344552 — Efron 1979, Annals of Statistics 7(1)
- 10.18653/v1/P18-1128 — Dror et al., ACL 2018, pp. 1383-1392
- 10.1145/1062455.1062502 — Fisler et al., ICSE 2005 (Crossref page field: 196)
- 10.1109/SP46214.2022.9833571 — Pearce et al., IEEE S&P 2022, pp. 754-768
- 10.1145/3597503.3639226 — Pan et al., ICSE 2024, pp. 1-13
- 10.1145/3729379 — AlphaTrans, PACMSE 2(FSE), pp. 2454-2476

## Crossref API title queries (https://api.crossref.org/works?query...)
- `query.title=PyMigBench Python Library Migration` — verified PyMigBench (10.1109/msr59073.2023.00075, MSR 2023, pp. 511-515) and, as a bonus, the ASE 2025 LLM library-migration study (10.1109/ase63991.2025.00077, pp. 867-879).
- `query.bibliographic=McKeeman Differential Testing for Software` — NO matching record found (only unrelated McKeeman papers). Result: **McKeeman 1998, "Differential Testing for Software" (Digital Technical Journal) — UNVERIFIED, EXCLUDED** from the verified CSV. Csmith (verified) is used as the differential-testing citation instead.

## ACL Anthology page fetch
- https://aclanthology.org/2025.naacl-long.194/ — confirmed CRMArena title, pages 3830-3850, DOI 10.18653/v1/2025.naacl-long.194.

## Excluded / not pursued
- McKeeman 1998 (differential testing) — UNVERIFIED via Crossref (see above); excluded.
- Venue claims not directly verified (e.g., ICLR acceptance of SWE-bench/AgentBench, NeurIPS for TransCoder/EvalPlus) were left as "arXiv preprint" in the CSV rather than asserted; only venues confirmed on a primary page (NAACL for CRMArena, EMNLP note on EnterpriseBench abs page, Crossref proceedings for DOI-verified entries) are recorded as venues.
- Search-result-only mentions (EnterpriseClawBench, Agent-Diff, EntCollabBench, COBOL-Coder, SEDCoT) were not independently verified against primary sources and were therefore not added to the CSV.
