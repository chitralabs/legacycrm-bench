# Excerpts from legacy_system/SYSTEM_OVERVIEW.md (Meridian CRM 4.2)

## 7. Batch jobs — semantics

`batch_jobs.cfg`: line format
`JOB <name> AT <HH:MM> RUN <script.crms> [ON_ERROR <ABORT|CONTINUE|RETRY:n>]`.
Jobs run sequentially in file order at their scheduled time; RETRY:n re-runs the whole
script up to n times; CONTINUE skips the failing row and logs `BATCH_ROWSKIP`.
