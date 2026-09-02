# Prompt template C1 — zero-shot (v1.0, frozen 2026-09-01)

Substitution variables: {TARGET_SPEC}, {LEGACY_ARTIFACTS} (each file rendered as
`--- FILE: <name> ---\n<content>`), {DELIVERABLES} (comma-separated file names).

---

You are migrating a customization from a legacy CRM system (Meridian CRM 4.2) to a modern
platform. Produce ONLY the deliverable file(s) named below, each in its own fenced block that
starts with ```file:<filename> and ends with ```. Do not output anything else.

Deliverables: {DELIVERABLES}

Target specification:

{TARGET_SPEC}

Legacy source artifacts:

{LEGACY_ARTIFACTS}
