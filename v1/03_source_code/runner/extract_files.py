#!/usr/bin/env python3
"""Extract deliverable files from a model response (```file:NAME fenced blocks)."""
import re

FENCE = re.compile(r"```file:([^\n`]+)\n(.*?)```", re.S)


def extract(response_text: str, expected: list[str]) -> tuple[dict, list]:
    """Returns ({filename: content}, notes). Only expected deliverable names are accepted;
    unexpected file blocks are recorded but not written (hallucinated-file signal)."""
    found, notes = {}, []
    for m in FENCE.finditer(response_text):
        name = m.group(1).strip()
        if name in expected:
            if name in found:
                notes.append(f"duplicate block for {name}; keeping last")
            found[name] = m.group(2)
        else:
            notes.append(f"unexpected file block ignored: {name}")
    for name in expected:
        if name not in found:
            notes.append(f"missing deliverable: {name}")
    return found, notes
