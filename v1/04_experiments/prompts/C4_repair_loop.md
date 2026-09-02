# Prompt template C4 — test-feedback repair (v1.0, frozen 2026-09-01)

Initial call: identical to C2. Repair calls (max 2) append:

---

Your previous migration failed acceptance testing. Failing checks (assertion details redacted):

{REDACTED_FAILURES}

Each line gives: test function name, and the assertion's message with all expected literal
values replaced by "<redacted>". Revise and output the complete corrected deliverable file(s)
again, in the same ```file:<name> fenced-block format. Output nothing else.

---

Redaction contract (runner/redact_failures.py): only the test nodeid and exception type are
passed verbatim; every literal operand in the assertion representation is replaced by
"<redacted>"; test source is never included. A leakage audit samples 10% of repair prompts
per run for manual inspection before analysis (logged in the run record).
