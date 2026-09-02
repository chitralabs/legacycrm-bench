#!/usr/bin/env python3
"""Prompt construction for conditions C1-C4 from the frozen templates (04_experiments/prompts).

Templates are markdown docs whose operative prompt text follows the first '---' line.
C1: base. C2: C1 + convention checklist before 'Target specification:'. C3: C2 + retrieved
SYSTEM_OVERVIEW sections (deterministic keyword retriever; choice logged). C4 initial = C2.
"""
import re
from pathlib import Path

V1 = Path(__file__).resolve().parent.parent.parent
PROMPTS = V1 / "04_experiments" / "prompts"
OVERVIEW = V1 / "02_benchmark_dataset" / "legacy_system" / "SYSTEM_OVERVIEW.md"

STOP = set("the a an and or of to in for with is are be as by on at from that this its must".split())


def _body(name: str) -> str:
    txt = (PROMPTS / name).read_text()
    return txt.split("\n---\n", 1)[1].strip()


def _checklist() -> str:
    return _body("C2_structured.md")


def overview_sections():
    txt = OVERVIEW.read_text()
    parts = re.split(r"\n(?=## )", txt)
    return [(p.splitlines()[0].lstrip("# ").strip(), p) for p in parts if p.startswith("## ")]


def _tokens(s: str):
    return {w for w in re.findall(r"[a-z]{3,}", s.lower())} - STOP


def retrieve_sections(target_spec: str, k: int = 3):
    """Deterministic top-k SYSTEM_OVERVIEW sections by token overlap; ties by document order."""
    spec_tokens = _tokens(target_spec)
    scored = []
    for idx, (title, body) in enumerate(overview_sections()):
        scored.append((len(spec_tokens & _tokens(body)), -idx, title, body))
    scored.sort(reverse=True)
    top = sorted(scored[:k], key=lambda t: -t[1])  # restore document order
    return [(t[2], t[3]) for t in top]


def legacy_blob(case_dir: Path) -> str:
    out = ""
    for f in sorted((case_dir / "legacy").rglob("*")):
        if f.is_file():
            out += f"--- FILE: {f.name} ---\n{f.read_text()}\n"
    return out


def build(case_dir: Path, condition: str, meta: dict) -> tuple[str, dict]:
    """Returns (prompt, log) where log records retrieval choices for the run record."""
    spec = (case_dir / "target_spec.md").read_text()
    prompt = _body("C1_zero_shot.md")
    prompt = prompt.replace("{DELIVERABLES}", ", ".join(meta["deliverables"]))
    prompt = prompt.replace("{TARGET_SPEC}", spec)
    prompt = prompt.replace("{LEGACY_ARTIFACTS}", legacy_blob(case_dir))
    log = {"condition": condition}
    if condition in ("C2", "C3", "C4"):
        prompt = prompt.replace("Target specification:",
                                _checklist() + "\n\nTarget specification:", 1)
    if condition == "C3":
        secs = retrieve_sections(spec)
        log["retrieved_sections"] = [t for t, _ in secs]
        ref = "Platform semantics reference (retrieved sections of the legacy platform "
        ref += "specification):\n\n" + "\n\n".join(b for _, b in secs)
        prompt = prompt.replace("Target specification:", ref + "\n\nTarget specification:", 1)
    return prompt, log
