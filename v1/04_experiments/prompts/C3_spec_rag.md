# Prompt template C3 — spec retrieval (v1.0, frozen 2026-09-01)

Same as C2 plus a "Platform semantics reference" section inserted after the checklist,
containing SYSTEM_OVERVIEW.md sections selected by the deterministic retriever
(runner/retrieve_spec.py, to be implemented): keyword overlap between target_spec.md and
section headings/bodies, top-3 sections, ties broken by document order. The retrieval choice
for every call is logged to the run record. No embedding or LLM-based retrieval is used, so
retrieval is exactly reproducible.
