# Zenodo Metadata Update Instructions (Phase 4)

Status 2026-09-16: **NOT YET CORRECTED — pending author action.** The live Zenodo record was
auto-created by the GitHub integration and lists the creator as the GitHub account name
"chitralabs" rather than the author. Nothing here changes or deletes any DOI; Zenodo
metadata edits create a new metadata revision of the same record.

## Live resources (verified reachable 2026-09-16)

- Repository: https://github.com/chitralabs/legacycrm-bench (release v0.1.1)
- Concept DOI: 10.5281/zenodo.22777518 · Version DOI: 10.5281/zenodo.22777519

## Target metadata

| Field | Value |
|---|---|
| Creator | Ganesan, Chitrapradha |
| Creator ORCID | 0009-0009-1305-1724 |
| Title | LegacyCRM-Bench: A Reproducible Benchmark for Evaluating LLM-Assisted Migration of Enterprise CRM Customizations |
| Version | v0.1.1 |
| Resource type | Software |
| Related identifier | https://github.com/chitralabs/legacycrm-bench/tree/v0.1.1 ("is supplement to" / "is identical to") |
| License | MIT (code) / CC BY 4.0 (data & specifications) — describe both in the description if the form allows one license field |

## Steps (≈3 minutes, in the author's browser, logged into Zenodo)

1. Open https://zenodo.org/records/22777519 (you must be logged in as the record owner).
2. Click **Edit** (creates a metadata draft; the DOI is unaffected).
3. Under **Creators**: replace "chitralabs" with family name "Ganesan", given name
   "Chitrapradha"; add ORCID 0009-0009-1305-1724.
4. Set **Resource type** to *Software*; confirm **Version** reads v0.1.1; set the Title as
   above if it differs.
5. Under **Related works / identifiers**: add
   `https://github.com/chitralabs/legacycrm-bench/tree/v0.1.1`.
6. **Save** and **Publish** the metadata revision. Verify the public page now shows the
   corrected creator.
7. Tell the assistant "Zenodo metadata updated" so the readiness record can note the live
   confirmation. Until the live record is re-checked, no project document claims the
   metadata is corrected.

Note: future GitHub releases will again auto-fill creator metadata from the repository; a
`.zenodo.json` file in the repository root can pin the correct creator for future releases —
ask the assistant to add one after this manual fix, so the correction persists.
