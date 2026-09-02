# IEEE Presentation / Copy Review — LegacyCRM-Bench draft v0.1

**Manuscript:** `07_manuscript/LegacyCRM_Bench_OJCS_v1.tex` (compiled PDF: 6 pages, IEEEtran journal class)
**Review role:** Simulated IEEE presentation/copy-editing reviewer (template, style, figures, tables, references, English)
**Review date:** 2026-09-01
**Style authorities used:** `00_project_admin/OJCS_CURRENT_REQUIREMENTS.md` (§§3, 5, 12: IEEE Author Center abstract rules, figure resolution/sizing, template requirement), IEEE Reference Guide conventions.
**Disclosure:** Internal pre-submission simulation.

---

## 1. Template compliance — REQUIRED FIX

- **PR-001 (Critical).** The manuscript uses `\documentclass[journal]{IEEEtran}` as an acknowledged stand-in (.tex lines 3–8). OJ-CS requires the official IEEE Open Journals template from template-selector.ieee.org, and the Computer Society states "Using an article template is required for journal submissions" (OJCS_CURRENT_REQUIREMENTS.md §12). This is blocker E9 in `04_experiments/EVIDENCE_REQUIRED.md`. The current 6-page length comfortably fits the 12-page limit, but pagination must be re-verified after porting; do not treat the IEEEtran page count as final.
- Related draft-state items that must be stripped at porting time: DRAFT watermark (lines 15–21); draft annotation embedded in `\title{}` including a date and an internal `Sec.~\ref{sec:results}` cross-reference (lines 27–28) — a `\ref` inside a title is improper in any IEEE template; author placeholder block (lines 32–35).

## 2. Abstract quality vs. IEEE rules

Verified by reading and counting (.tex lines 39–57):

- Length: **196 words** — within the 250-word IEEE Author Center limit. PASS.
- Single paragraph: yes. No references, no equations, no math symbols, no footnotes: PASS.
- Abbreviations: the abstract uses CRM and LLM (both expanded at first use inside the abstract). IEEE Author Center guidance says the abstract should be "without abbreviations" (OJCS_CURRENT_REQUIREMENTS.md §3); defined-at-first-use is common practice and usually tolerated, but strictly this deviates — Editorial-level flag (PR-011). The title also contains "LLM" and "CRM"; abbreviations in titles are discouraged but widespread; left to author judgment.
- Content defect (shared with the desk review): "are released for independent reproduction" (line 54) is untrue while the repository/DOI are placeholders (lines 393–394, 419–420) — logged as the desk review's ED-003; not duplicated here.
- English: the opening sentence (lines 40–43) is a 44-word double-conjunction sentence ("must migrate a customization layer, including ..., and large language models (LLMs) are increasingly proposed...") — grammatical but overloaded; split it (PR-013, Editorial).
- IEEEkeywords (lines 59–62): **8 keywords** against the IEEE Author Center's "3–5 keywords or phrases" guidance — trim (PR-012, Editorial). Capitalization is also inconsistent ("Benchmark, large language models, ... CRM").

## 3. Structure and English clarity

- Structure is complete and logical (Intro → Related → Gap/Contributions → RQs → Design goals → Taxonomy → Dataset → Oracles → Setup → Results → Ablation → Failure analysis → Discussion → Implications → Threats → Ethics → Repro → Limitations → Conclusion), but **17 numbered sections in a 6-page paper** is fragmentary for IEEE journal style; Sections III–V (Gap/Contributions, RQs, Design Goals) and XI–XIV (Ablation, Failure, Discussion, Implications) are candidates for consolidation into fewer top-level sections with subsections (PR-014, Editorial).
- English is clear, precise, and largely typo-free; no grammatical errors found beyond the run-on noted above. LaTeX conventions (``quotes'', `\emph`, `1{,}700`, `pass\textasciicircum{}$k$`) are used correctly.
- Sections XI ("Planned, not executed", lines 330–335) and parts of XIII–XIV are placeholders for future results; in an IEEE journal article, sections that contain no executed content should not exist as numbered sections — presentation symptom of the substantive readiness problem.

## 4. Figure quality — F1

`06_figures_tables/F1_instrument_validation.pdf` (vector, Matplotlib 3.11.1, MediaBox 515.52 x 208.8 pt = 7.16 in x 2.9 in) and the PNG sibling (2864x1160 px @ ~400 dpi). Verified by rendering both.

- **PR-002 (Major) — the figure is clipped.** In both PDF and PNG: left y-axis category labels are truncated at the canvas edge ("Batch processing" -> "atch processing", "Referential integrity" -> "erential integrity", "Schema mapping" -> "chema mapping", "Config. modernization" -> "g. modernization"); the bottom panel captions "(a) Acceptance tests per category" and "(b) Mutation kill rate (%)" are cut off mid-glyph; and a stray red rectangle artifact sits in the top-left corner. Regenerate in `03_source_code/analysis/make_figures.py` with proper margins (`bbox_inches='tight'` or explicit `subplots_adjust`) and remove the stray artifact.
- **PR-003 (Major) — width mismatch.** The figure is authored at 7.16 in (IEEE double-column width) but included at `width=\columnwidth` (~3.5 in) in a single-column float (.tex line 310), scaling all text to roughly 50% — tick labels will render around 4–5 pt, below legible/IEEE-acceptable size. Either regenerate at 3.5 in with fonts sized for single-column, or promote to `figure*`.
- Resolution/format: vector PDF satisfies IEEE's preference; the 400-dpi PNG exceeds the >300 dpi raster requirement. PASS on format, once clipping is fixed.
- Accessibility: single-hue bars with numeric value labels — no color-only encoding; acceptable.
- **PR-009 (Minor) — path portability.** `\includegraphics{../06_figures_tables/F1_instrument_validation.pdf}` reaches outside the manuscript directory; OJ-CS requires figures submitted individually (CFP, OJCS_CURRENT_REQUIREMENTS.md §5) and the compiled package must be self-contained. Copy the figure into `07_manuscript/` (or a `figures/` subdirectory) at packaging time.

## 5. Table consistency

Checked wrapper tables (.tex lines 212–222, 316–327) against `07_manuscript/generated/T1_composition.tex`, `T2_validation.tex`, `numbers.tex`, and the CSVs in `06_figures_tables/`:

- Column counts match specs (`lccccc`, 6 columns) in both tables; totals are internally consistent (36 cases = 12x3; per-category tests sum to 505; 335/363 = 92.3%). Abstract/Results macros match `numbers.tex` exactly (ledger C012). PASS.
- **PR-010 (Editorial).** Table I's generated body has no `\midrule` before its Total row, while Table II's does (`T1_composition.tex` vs `T2_validation.tex` last rows) — inconsistent rule usage between the two tables; fix in `make_tex_tables.py`.
- **PR-015 (Editorial).** "716 rows across ten CSVs" (.tex line 245) is hard-coded prose, outside the `numbers.tex` macro-injection discipline the file header promises (lines 6–7). It is ledger-verified (C006) but should be macro-injected for consistency of the stated policy.

## 6. Acronyms at first use

- CRM: expanded at first use in abstract (line 40) and implicitly in body text ("Customer relationship management platforms", line 67) — acceptable, though IEEE convention is to re-define formally at first body use since abstracts must stand alone. LLM: expanded in abstract (line 42); first body use "LLM assistance" (line 72) never re-expanded — same Minor point (PR-008).
- RBAC: expanded at first body use, "role-based access-control (RBAC)" (lines 68–69). PASS.
- **DSL: never expanded anywhere** (first use "validation-rule DSL", line 91) — define "domain-specific language (DSL)". **AST: never expanded** (first use "First-order AST mutations", line 297) — define "abstract syntax tree (AST)". Both in PR-008 (Minor).
- VRL: defined at line 231 ("validation-rule DSL (VRL)") but the acronym is never used again — drop the parenthetical or use it (PR-008).
- SQL, XML, INI, JSON, CSV, MIT, CC BY: on IEEE's commonly-accepted list or product/license names; no expansion required. `pass^k` is attributed to τ-bench at first use (line 120). PASS.

## 7. References (`07_manuscript/refs.bib`, 38 entries, generated from REFERENCE_VERIFICATION.csv)

- **PR-004 (Major) — silently truncated author lists.** Several entries list only the first N authors with no `and others` (BibTeX for "et al."): `chen2021humaneval` (6 listed; the paper has ~58 authors), `lu2021codexglue` (8 of 20+), `zhuo2024bigcodebench` (6 of many), `bhatt2023cyberseceval` (7), `bhatt2024cyberseceval2` (6), `liu2023agentbench` (10), `drouin2024workarena` (10), `diggs2024legacy` (10), `hans2025coboltesting` (10), `zhu2025rigorous` (10). As generated, IEEEtran will typeset these as if the listed authors were the complete set — a factual misattribution, not just style. Fix in `03_source_code/analysis/make_bib.py`: append `and others` when the source list is truncated (IEEE style then renders "et al.").
- **PR-005 (Minor) — arXiv entries where a version of record exists.** IEEE Reference Guide *does* have an accepted arXiv citation format, so arXiv-only entries are acceptable IEEE style **for genuinely unpublished preprints** — the design decision is defensible for those. But entries whose venues are known should cite the version of record: `vishwakarma2025enterprisebench` (EMNLP 2025 — stated only in `note`), `jimenez2024swebench` (ICLR 2024 — stated only in `note`), and, per the project's own PRIOR_WORK_NOTES basis, `lachaux2020transcoder` (NeurIPS 2020), `liu2023evalplus` (NeurIPS 2023), `yao2024taubench` (ICLR 2025), `styles2024workbench`, `liu2023repobench` (ICLR 2024), `jain2024livecodebench` (ICLR 2025), `golchin2024timetravel` (ICLR 2024). Moving venue from `note` to a proper `booktitle` also fixes the odd rendered strings like "EMNLP 2025 (Main Track, per arXiv listing); arXiv preprint".
- **PR-006 (Minor) — incomplete fields.** `efron1979bootstrap` lacks pages (1–26); `fisler2005margrave` gives `pages = {196}` where the paper spans 196–205; arXiv `@misc` entries carry no DOI or URL — IEEE's arXiv format expects the arXiv identifier to be visible in the rendered reference (IEEEtran renders `eprint` only with certain styles; verify the compiled bibliography actually shows "arXiv:2505.18878" etc., otherwise add `howpublished`/`note` URLs).
- Completeness of coverage: all 38 `\cite` keys in the .tex resolve to entries in refs.bib (spot-verified; counts match), no uncited entries observed, and provenance is traceable via the ledger (C008). PASS.

## 8. Defect list (all registered in `issues_editorial.csv` with IDs PR-001 … PR-015)

| ID | Severity | Location | Defect |
|----|----------|----------|--------|
| PR-001 | Critical | .tex lines 3–8 | IEEEtran stand-in, not official IEEE Open Journals template (blocker E9) |
| PR-002 | Major | 06_figures_tables/F1_instrument_validation.pdf/.png | Clipped y-labels, clipped panel captions, stray red artifact |
| PR-003 | Major | .tex line 310 + F1 MediaBox | 7.16-in figure included at \columnwidth: fonts scaled to ~50% |
| PR-004 | Major | refs.bib (10 entries listed above) | Truncated author lists without "and others" (misattribution) |
| PR-005 | Minor | refs.bib (9 entries listed above) | Published works cited as arXiv preprints; venue only in `note` |
| PR-006 | Minor | refs.bib efron1979bootstrap, fisler2005margrave | Missing/incorrect page ranges; arXiv ID rendering unverified |
| PR-007 | Minor | .tex lines 15–35 | Watermark, `\ref` and date inside title, author placeholder — must be stripped |
| PR-008 | Minor | .tex lines 91, 297, 231, 67, 72 | DSL and AST never expanded; VRL defined but unused; CRM/LLM not re-expanded in body |
| PR-009 | Minor | .tex line 310 | Figure included via ../ relative path; package not self-contained |
| PR-010 | Editorial | generated/T1_composition.tex vs T2_validation.tex | Inconsistent \midrule before Total rows |
| PR-011 | Editorial | .tex lines 39–57 | Abbreviations in abstract vs IEEE "without abbreviations" guidance |
| PR-012 | Editorial | .tex lines 59–62 | 8 keywords vs IEEE 3–5 guidance; inconsistent capitalization |
| PR-013 | Editorial | .tex lines 40–43 | 44-word run-on opening sentence of abstract |
| PR-014 | Editorial | whole .tex | 17 numbered sections in 6 pages; consolidate; empty "planned" sections XI |
| PR-015 | Editorial | .tex line 245 | "716 rows" hard-coded outside numbers.tex macro discipline |

**What is in good shape:** abstract length (196/250), no refs/equations in abstract, macro-injected numbers all consistent with generated tables and the claim ledger, vector figure format and raster resolution, RBAC defined at first use, LaTeX hygiene, 38/38 citations resolving, AI-use disclosure present in Acknowledgments identifying the system and the areas of use (consistent with the IEEE AI-disclosure policy in OJCS_CURRENT_REQUIREMENTS.md §8).
