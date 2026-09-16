# IEEE Open Journal of the Computer Society (OJ-CS) — Current Author Requirements, Re-Verified

**Access date for ALL sources: 2026-09-16** (fresh re-verification for final pre-submission audit)

**Sources policy:** Official IEEE / IEEE Computer Society pages only (computer.org, ieee.org, open.ieee.org, journals.ieeeauthorcenter.ieee.org, ieeexplore.ieee.org, template-selector.ieee.org). Facts below are paraphrased from those pages; each carries its source URL.

**Access-method notes (important for reproducibility):**
- The OJ-CS pages on computer.org/csdl are JavaScript-rendered. Plain HTTP fetches return only an empty shell titled "CSDL | IEEE Computer Society"; content was verified in a real rendered browser session on 2026-09-16.
- **IEEE Xplore blocks automated access.** Both a plain fetch and a rendered browser session to the OJ-CS Xplore home (https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=8782664) returned an IEEE error page reading "IEEE Xplore - Unable to Load Page, Error Code: 418" (bot rejection). Nothing in this audit therefore rests on Xplore-only content; all items were verified on other official IEEE properties. If Xplore-hosted metadata must be checked, do it manually in a normal browser.

---

## 1. Page limit

**Finding:** The OJ-CS Author Information page states the page limit is **12 double-column pages for regular papers and 20 double-column pages for survey papers**. (Source: https://www.computer.org/csdl/journal/oj/write-for-us/75639 — rendered in browser, accessed 2026-09-16)

- **Hard vs soft: NOT STATED.** No official OJ-CS page found states whether the limit is strict, whether references/biographies count, or whether overlength page charges exist (unlike some IEEE CS Transactions, which publish explicit overlength policies). Treat 12 pages (regular) as a hard planning ceiling; see UNVERIFIED.
- Note: the separate OJ-CS Call-for-Papers page still says only 12 double-column pages, with no survey-paper tier — see CONFLICTS. (Source: https://www.computer.org/digital-library/journals/oj/cfp-open-journal, accessed 2026-09-16)

## 2. Required template

**Finding:** OJ-CS instructs authors to format using the **IEEE Open Journals article template** (Word and LaTeX versions), obtained via the IEEE Author Center. (Source: https://www.computer.org/csdl/journal/oj/write-for-us/75639, accessed 2026-09-16)

- The IEEE Author Center's templates page directs authors to the interactive **IEEE Template Selector** (https://template-selector.ieee.org/). (Source: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates/, accessed 2026-09-16)
- Walked the Template Selector on 2026-09-16 (Transactions/Journals/Letters → IEEE Open Journal of the Computer Society → All → format). It serves, for OJ-CS original research articles:
  - Word: **IEEE-open-journal-template.doc**
  - LaTeX: **IEEE-open-journal-template.zip** (template metadata last modified 2024-10-15 per the selector's API)
  (Source: https://template-selector.ieee.org/ — selector API response `api/ieee-template-selector/template/publication-type/1/publication-title/210/article/2`, accessed 2026-09-16)
- **LaTeX class name: NOT STATED on any official page checked** — it is only discoverable inside the zip. See UNVERIFIED.
- Note: the OJ-CS page's deep link to "templates-for-ieee-open-journals" on the Author Center now 301-redirects to the generic IEEE Article Templates page; the Template Selector is the canonical route. (Verified 2026-09-16)

## 3. Abstract word limit

Three official data points; **no OJ-CS-specific number exists**:

1. **IEEE Author Center (generic, the page OJ-CS delegates to):** abstract must be a single paragraph of **up to 250 words**, self-contained, no abbreviations/footnotes/references/math, with 3–5 keywords. (Source: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/, accessed 2026-09-16)
2. **IEEE Editorial Style Manual for Authors (PDF, p. 5):** abstract must be one paragraph of **150–250 words**. (Source: https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE-Editorial-Style-Manual-for-Authors.pdf, accessed 2026-09-16)
3. **IEEE Computer Society author guidelines (CS-wide):** journal abstracts of **100–200 words** for regular/special-issue papers (50 for short papers). (Source: https://www.computer.org/publications/author-resources/authors, accessed 2026-09-16)

The OJ-CS Author Information page itself sets no number; it refers authors to the IEEE Author Center for abstract guidance. **The template's own internally stated range could not be checked without downloading the template — see UNVERIFIED.** See CONFLICTS for which to follow (practical answer: 150–200 words satisfies every official statement simultaneously).

## 4. Accepted manuscript formats; figures + resolution

**Manuscript text:** submit in **PDF, DOC, or LaTeX** format. (Source: https://www.computer.org/csdl/journal/oj/write-for-us/75639, accessed 2026-09-16)

**Figures (OJ-CS-specific):** submit figures **individually** in **PS, EPS, PDF, PNG, or TIF**. (Source: https://www.computer.org/csdl/journal/oj/write-for-us/75639, accessed 2026-09-16)

**Figure formats (IEEE Author Center, generic):** PS, EPS, PDF, PNG, or TIFF; Office formats (DOC/PPT/XLS) only if the graphic originated there; author photos may be high-resolution JPEG. (Source: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/file-formatting/, accessed 2026-09-16)

**Resolution (IEEE Author Center):** black-and-white line art **greater than 600 dpi**; color and grayscale images **greater than 300 dpi**. Recommended widths: 3.5 in (single column) / 7.16 in (double column). IEEE's graphics checker: http://graphicsqc.ieee.org/. (Sources: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/resolution-and-size/ and .../file-formatting/, accessed 2026-09-16)

## 5. Submission portal

**Finding:** OJ-CS accepts submissions through the **IEEE Author Portal**. The "IEEE Author Portal" link on the OJ-CS Author Information page resolves to **https://ieee.atyponrex.com/journal/oj-cs** (link href captured from the rendered page on 2026-09-16). (Source: https://www.computer.org/csdl/journal/oj/write-for-us/75639, accessed 2026-09-16)

- Not ScholarOne. The CS-wide author page still describes ScholarOne Manuscripts as the review system for most CS periodicals and notes the migration to the IEEE Author Portal is in progress — for OJ-CS specifically the journal's own page already names the Author Portal. (Source: https://www.computer.org/publications/author-resources/authors, accessed 2026-09-16)

## 6. Supplementary material

**OJ-CS-specific:** the CFP encourages uploading datasets to **IEEE DataPort**, stating it strengthens the paper and supports reproducibility. (Source: https://www.computer.org/digital-library/journals/oj/cfp-open-journal, accessed 2026-09-16)

**IEEE Author Center (generic journal guidance)** (Source: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/prepare-supplementary-materials/, accessed 2026-09-16):
- Recommended formats — Text: TXT, DOC, DOCX, PDF. Image: JPG, TIF, PNG, GIF, PDF, PS, EPS, BMP. Video: MP4, MOV, WMV, AVI. Audio: MP3, AIFF, MOV, RA, WAV.
- Files must be labeled as supplementary and uploaded as **separate files** during submission (CS guidance also requires supplemental files be separate from the main paper PDF — Source: https://www.computer.org/publications/author-resources/authors).
- **README required for datasets and for supplementary material packages** (PDF or text), covering: overall description, total size, platform/environment, packing list of components, setup/run instructions, expected output, and contact information.
- Size caps stated: video limited to **100 MB** (reduce resolution if larger); graphical abstract image < 45 KB (660×295 px), graphical-abstract video < 100 MB, audio < 3 MB.

## 7. ORCID requirement

**Finding: ORCID is required.** The IEEE Editorial Style Manual for Authors (p. 6) states ORCIDs are requested for **all authors** and **required for the corresponding author** in order to submit a paper for peer review and to access the article proof at the Author Gateway. (Source: https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE-Editorial-Style-Manual-for-Authors.pdf, accessed 2026-09-16)

- IEEE Computer Society guidance likewise says the submission system prompts for an ORCID, which is required by all IEEE publications. (Source: https://www.computer.org/publications/author-resources/authors, accessed 2026-09-16)

## 8. Generative-AI disclosure policy

**Finding:** Per the IEEE Submission Policies (Section: Guidelines for Artificial Intelligence (AI)-Generated Content), use of AI-generated content in an article — text, figures, images, and code included — "shall be disclosed in the acknowledgments section" (IEEE Author Center, Submission and Peer Review Policies). The policy further requires that the AI system used be identified, that the specific sections containing AI-generated content be identified, and that a brief explanation be given of the level at which the AI system was used. AI use for editing and grammar enhancement is treated as outside the policy's intent: disclosure is not required, but recommended. Reviewers must not process manuscript content through public AI platforms (confidentiality breach). The page also points to the IEEE Principles of Ethical Use of AI in Publishing in the PSPB Operations Manual (pp. 5–6). (Source: https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/, accessed 2026-09-16)

## 9. Open-access APC (2026)

**Finding (OJ-CS-specific):** **US$2,160, effective 1 January 2026.** IEEE members receive a 5% discount; IEEE Society members receive a 20% discount; the discounts cannot be combined. Corresponding authors from low-income countries are eligible for waived or reduced APCs. The APC is paid after acceptance. (Source: https://www.computer.org/csdl/journal/oj/write-for-us/75639, accessed 2026-09-16)

- Corroborated IEEE-wide: for 2026 the APC for the majority of IEEE's fully open access journals is $2,160, with the same 20%/5% member discounts (discounts not applicable to undergraduate/graduate students). (Source: https://open.ieee.org/for-authors/article-processing-charges/, accessed 2026-09-16)

## 10. Author biography / photograph at initial submission

**Finding: not required at initial submission.**
- CS-wide author guidelines: for journals, author biographies are **not required** (no set style); author **photos** appear in the checklist of **final** materials submitted **after acceptance** (photos apply to full-length journal articles). (Source: https://www.computer.org/publications/author-resources/authors, accessed 2026-09-16)
- IEEE Editorial Style Manual (p. 16): even at publication, an author may opt out of publishing a biography/photograph (a one-line "squib" is then used, or nothing if all authors opt out). (Source: https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE-Editorial-Style-Manual-for-Authors.pdf, accessed 2026-09-16)
- No OJ-CS-specific statement requiring a bio/photo at initial submission was found on any official page checked.

## 11. Peer-review process and turnaround

**OJ-CS-specific expedited schedule** (Source: https://www.computer.org/publications/peer-review-schedules — section "Open Journal", accessed 2026-09-16; verbatim text captured from the served HTML):
- The rapid peer-review process has a publication time frame of **10 weeks** for most accepted papers — **there is no revision option for submissions**.
- Editors have **1 day** to assign reviewers; reviewers get **1 week** to review; editors have **1 day** to submit a recommendation.
- The page explicitly excludes OJ-CS from the regular-paper schedule (which allows 4–12 week major and 1–4 week minor revisions).

**Implication:** unlike ordinary IEEE CS journals (whose decision set includes Accept / Minor Revision / Major Revision / Revise-and-Resubmit / Reject — Source: https://www.computer.org/publications/making-peer-review-recommendations, accessed 2026-09-16), OJ-CS's own published schedule provides **no revision round**: plan for effectively accept-or-reject, with a rejected paper needing a fresh submission. Submit a manuscript that is final-quality on arrival.

**Review-integrity parameters (OJ-CS page):** peer review follows IEEE PSPB Operations Manual §§8.2.1.C & 8.2.2.A; minimum **two independent reviewers**; **single-anonymous** review; plagiarism screening before acceptance. (Source: https://www.computer.org/csdl/journal/oj/write-for-us/75639, accessed 2026-09-16)

**Published turnaround statements conflict (5 vs 10 weeks)** — see CONFLICTS. The About page and CFP still advertise rapid publication targeting **5 weeks** for most accepted papers. (Sources: https://www.computer.org/csdl/journal/oj/about/75633 and https://www.computer.org/digital-library/journals/oj/cfp-open-journal, accessed 2026-09-16)

---

## CONFLICTS (with resolution: most publication-specific and current wins)

1. **Page limit — 12 only vs 12/20.** CFP page (https://www.computer.org/digital-library/journals/oj/cfp-open-journal): 12 double-column pages, no survey tier. OJ-CS Author Information page (https://www.computer.org/csdl/journal/oj/write-for-us/75639): 12 regular / 20 survey. **Follow the Author Information page** — it is the journal's operative author-instructions page and is demonstrably the more current of the two (it already carries the 1 Jan 2026 APC), whereas the CFP text matches older copy. For a regular paper both agree: 12 double-column pages.

2. **Abstract length — 250 vs 150–250 vs 100–200.** Generic IEEE Author Center: up to 250 words; IEEE Style Manual: 150–250; IEEE CS-wide author page: 100–200 for journal regular papers. No OJ-CS-specific figure. **Resolution:** the OJ-CS page delegates abstract guidance explicitly to the IEEE Author Center, so the 250-word cap governs formal compliance; but since the CS-wide guideline (100–200) also claims scope over CS journals, the risk-free pre-submission choice is an abstract of **150–200 words**, which satisfies every official statement at once.

3. **Turnaround — 5 weeks vs 10 weeks.** OJ-CS About page and CFP: publication time frame of 5 weeks for most accepted papers. CS Peer Review Schedules page (Open Journal section): 10 weeks for most accepted papers. Both are official and OJ-CS-specific. **Follow the Peer Review Schedules page (10 weeks) for planning** — it is the operational scheduling document with stage-by-stage deadlines, while the 5-week figure appears in promotional/About copy; expect reality between the two.

4. **Revision availability — revisions vs none.** CS-wide decision guidance lists minor/major revision decisions for CS journals; the OJ-CS-specific entry on the Peer Review Schedules page says there is no revision option for OJ-CS submissions. **Follow the OJ-CS-specific statement: no revision round.**

5. **Submission system — ScholarOne vs IEEE Author Portal.** CS-wide author page still describes ScholarOne (noting migration in progress); the OJ-CS Author Information page names the IEEE Author Portal, linking to https://ieee.atyponrex.com/journal/oj-cs. **Follow the OJ-CS page: IEEE Author Portal.**

---

## UNVERIFIED (with exact next steps)

1. **Whether the 12-page (regular) / 20-page (survey) limit is hard or soft, and any overlength charges.** Not stated on the OJ-CS Author Information page, CFP, or About page, nor in CS-wide author guidelines for this journal. Next step: email the OJ-CS editorial office via the Editor-in-Chief listed on the About page — Vincenzo Piuri, University of Milan, vincenzo.piuri@unimi.it (Source for contact: https://www.computer.org/csdl/journal/oj/about/75633, accessed 2026-09-16) — or ask IEEE CS publications staff via the contact page at https://www.computer.org/about/contact.

2. **LaTeX class name inside the official OJ-CS template.** The Template Selector serves IEEE-open-journal-template.zip for OJ-CS but no official page states the .cls name. Next step: download that zip from https://template-selector.ieee.org/ (Transactions, Journals and Letters → IEEE Open Journal of the Computer Society → All → LaTeX) and read the class file name from the zip and the \documentclass line of the sample .tex. (Deliberately not downloaded during this automated audit.)

3. **The template's own internally stated abstract range** (the Word template text typically states an abstract length). Next step: same download as item 2 (Word variant: IEEE-open-journal-template.doc) and check the abstract instructions inside.

4. **Per-file upload size cap of the IEEE Author Portal for OJ-CS supplementary files** (beyond the IEEE-wide 100 MB video guidance). Not published on the pages checked. Next step: check the file-upload screen at https://ieee.atyponrex.com/journal/oj-cs during actual submission, or ask IEEE Publications Support via https://supportcenter.ieee.org.

5. **Whether every co-author (vs corresponding author only) must supply an ORCID in the Author Portal for OJ-CS.** The Style Manual says requested for all, required for the corresponding author; portal behavior for co-authors not verifiable without a live submission account. Next step: confirm on the author details screen at https://ieee.atyponrex.com/journal/oj-cs.

6. **IEEE Xplore-hosted OJ-CS "Author Resources" content.** Unverifiable by automation: https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=8782664 returned IEEE's "Unable to Load Page / Error Code: 418" bot-block on 2026-09-16 (both fetch and rendered browser). Next step: open that URL manually in a normal browser if Xplore-side confirmation is desired; all items above are already covered by non-Xplore official sources.

---

*Audit performed 2026-09-16. All URLs accessed 2026-09-16. Rendered-browser verification used for computer.org/csdl pages and template-selector.ieee.org (JavaScript applications); all other pages fetched directly.*
