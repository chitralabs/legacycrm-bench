# Public Release Manifest (artifact hygiene)

When packaging the public artifact (repository + archival deposit), INCLUDE `v1/` except:

- `.venv/` (environment; reproducers build their own from `03_source_code/requirements.txt`)
- `**/__pycache__/`, `*.pyc`
- `05_results/repro_*.jsonl` (reproducer outputs, not archived evidence)
- `11_archived_drafts/` (internal backups)
- `09_peer_review_audit/` — internal review materials; release decision belongs to the authors
  (recommended: release, since the audit loop is part of the paper's method claims)
- `10_submission_package/COVER_LETTER_DRAFT.md` (correspondence, not artifact)

Verify before release: `shasum -a 256 -c 05_results/SHA256SUMS`; run the reproduction guide
end-to-end on a second machine (open blocker); confirm no credential patterns
(`grep -rE "sk-[A-Za-z0-9]|api_key\s*=" --include="*.py" --include="*.json" v1/` should hit
only vault:// references and documentation).
