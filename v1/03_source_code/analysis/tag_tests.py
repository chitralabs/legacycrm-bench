#!/usr/bin/env python3
"""RQ2 property-tagging: generate the DRAFT per-test tag map (LegacyCRM-Bench).

Walks every case's ``tests/test_acceptance.py`` under
``02_benchmark_dataset/cases/<category>/<CASE-ID>/``, extracts each test
function via the AST, and proposes one of six property classes per test:

    functional | ordering_rounding | security | privacy | audit |
    completeness_hallucination

Proposals combine (a) name-token heuristics with (b) inspection of the test's
actual source segment (docstring, comments, assert content), per
04_experiments/EXPERIMENT_PLAN.md ("Preservation-property tagging") and
STUDY_PROTOCOL.md section 5 / Amendment A1.  The output,
``05_results/test_tags_draft.csv``, is a DRAFT ONLY: every row must be
manually reviewed; the frozen map is ``05_results/test_tags.csv``.

Stdlib only.  Usage:  python3 tag_tests.py
"""
from __future__ import annotations

import ast
import csv
import re
import sys
from pathlib import Path

V1_ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = V1_ROOT / "02_benchmark_dataset" / "cases"
OUT_CSV = V1_ROOT / "05_results" / "test_tags_draft.csv"

CLASSES = (
    "functional",
    "ordering_rounding",
    "security",
    "privacy",
    "audit",
    "completeness_hallucination",
)


def tokens_of(name: str) -> set[str]:
    return set(name.lower().split("_"))


def comment_text(segment: str) -> str:
    """All '#' comment text inside the function's source segment."""
    out = []
    for line in segment.splitlines():
        if "#" in line:
            out.append(line.split("#", 1)[1])
    return " ".join(out)


def evidence_blob(name: str, segment: str, docstring: str) -> str:
    """Lower-cased pool of evidence: name + docstring + comments + body."""
    return " ".join([name, docstring or "", comment_text(segment), segment]).lower()


def propose(name: str, segment: str, docstring: str) -> tuple[str, str]:
    """Return (proposed_class, rationale).

    Order of checks is most-specific-first; each check requires either a
    corroborating token in the body (docstring/comment/assert content) or an
    unambiguous name token, so classification is never name-tokens-alone.
    """
    n = name.lower()
    toks = tokens_of(n)
    blob = evidence_blob(name, segment, docstring)

    # --- security -----------------------------------------------------------
    if "forbidden" in blob and "import" in blob:
        return "security", "scans deliverable source for forbidden imports"
    if re.search(r"credential|secret_ref|password|vault", blob) and (
        "credential" in blob or "secret" in blob
    ):
        return "security", "asserts credential/secret handling (no literal secrets)"
    rbac_body = re.search(r"\.can\(|privilege|widening|role_permissions", blob)
    rbac_name = toks & {"denies", "deny", "denied", "grants", "grant", "scope",
                       "rbac", "widening", "privilege", "role", "bypasses"}
    if rbac_body and (rbac_name or re.search(r"deny|allow|grant|scope", blob)):
        return "security", "RBAC access decision (deny/grant/scope) asserted via can()"
    if rbac_name and re.search(r"is (True|False)|== (True|False)|deny|authoriz", segment):
        return "security", "asserts role-based allow/deny authorization decision"

    # --- privacy ------------------------------------------------------------
    optout = re.search(r"opt[_-]?out|opted[_-]?out|optout_flg", blob)
    payloadish = re.search(r"payload|export|outbound|not in |never in|excluded", blob)
    if optout and payloadish:
        return "privacy", "asserts opt-out handling for outbound payload inclusion/exclusion"
    if re.search(r"soft[_ ]?deleted", blob) and re.search(
        r"payload|outbound|export", blob
    ) and re.search(r"excluded|not in |never", blob):
        return "privacy", "asserts soft-deleted record excluded from outbound payload"
    if optout:
        return "privacy", "test exercises opt-out flag semantics"

    # --- audit --------------------------------------------------------------
    audit_body = re.search(r"aud_event|audit|append", blob)
    if audit_body and re.search(r"emit|audits|audit(ed)?\b|aud_event", blob):
        if toks & {"audit", "audited", "audits", "emits", "emit"} or re.search(
            r"aud_event|emits|no_audit|audit_config", blob
        ):
            return "audit", "asserts audit event emission/suppression or audited-set content"
    if re.search(r"append[- _]only|no_update_or_delete|defensive copy", blob) or (
        "append" in toks and "store" in blob
    ):
        return "audit", "asserts append-only audit store surface"

    # --- completeness / hallucination --------------------------------------
    if re.search(r"invent|hallucinat", blob):
        return "completeness_hallucination", "asserts no invented/hallucinated elements"
    if re.search(r"round[_ ]?trip", blob):
        return "completeness_hallucination", "round-trip completeness assertion"
    if re.search(r"completeness|no .*(dropped|missing)|all .*present|exact(ly)? the", blob) and re.search(
        r"set\(|== \{|sorted\(|keys\(\)|len\(", segment
    ):
        return "completeness_hallucination", "asserts exact/complete element set (nothing missing or extra)"
    if toks & {"exact", "exactly"} and re.search(r"keys|set|schema|shape", blob):
        return "completeness_hallucination", "asserts exact key/element set"

    # --- ordering / rounding ------------------------------------------------
    if re.search(r"half[_ ]?up|round(ing|ed|s)?\b|banker", blob) and re.search(
        r"decimal|cent|round|0\.5|minor", blob
    ):
        return "ordering_rounding", "asserts rounding behavior (half-up/precision)"
    order_name = toks & {"order", "ordered", "ordering", "sorted", "renumber",
                         "renumbering", "contiguous", "sequence", "first",
                         "ascending", "before"}
    if order_name and re.search(r"order|sort|ascending|index|\[0\]|first|before", blob):
        return "ordering_rounding", "asserts element/evaluation ordering"
    if re.search(r"file order|document order|preserves? .*order|in_file_order", blob):
        return "ordering_rounding", "asserts source-order preservation"

    # --- default ------------------------------------------------------------
    return "functional", "behavioral/value assertion with no specific property tokens"


def iter_case_dirs():
    for category_dir in sorted(p for p in CASES_DIR.iterdir() if p.is_dir()):
        if category_dir.name == "__pycache__":
            continue
        for case_dir in sorted(p for p in category_dir.iterdir() if p.is_dir()):
            test_file = case_dir / "tests" / "test_acceptance.py"
            if test_file.is_file():
                yield category_dir.name, case_dir.name, test_file


def main() -> int:
    rows = []
    for category, case_id, test_file in iter_case_dirs():
        src = test_file.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                segment = ast.get_source_segment(src, node) or ""
                doc = ast.get_docstring(node) or ""
                proposed, rationale = propose(node.name, segment, doc)
                assert proposed in CLASSES
                rows.append({
                    "case_id": case_id,
                    "category": category,
                    "test_name": node.name,
                    "proposed_class": proposed,
                    "rationale": rationale,
                })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["case_id", "category", "test_name", "proposed_class", "rationale"]
        )
        writer.writeheader()
        writer.writerows(rows)

    counts = {}
    for r in rows:
        counts[r["proposed_class"]] = counts.get(r["proposed_class"], 0) + 1
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")
    for cls in CLASSES:
        print(f"  {cls}: {counts.get(cls, 0)}")
    print("DRAFT ONLY - every row requires manual review (frozen map: test_tags.csv).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
