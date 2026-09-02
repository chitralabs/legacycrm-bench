#!/usr/bin/env python3
"""Generate 07_manuscript/refs.bib from 01_literature/REFERENCE_VERIFICATION.csv.

Only rows with status VERIFIED are emitted, so the bibliography cannot contain an
unverified reference by construction.
"""
import csv
from pathlib import Path

V1 = Path(__file__).resolve().parent.parent.parent
SRC = V1 / "01_literature" / "REFERENCE_VERIFICATION.csv"
DST = V1 / "07_manuscript" / "refs.bib"


def bib_authors(s):
    names = [a.strip() for a in s.split(";") if a.strip()]
    truncated = "et al." in names
    names = [n for n in names if n != "et al."]
    # a CSV author list ending in "et al." must become BibTeX "and others",
    # otherwise the bibliography silently misattributes the work to fewer authors
    return " and ".join(names) + (" and others" if truncated else "")


def esc(s):
    return s.replace("&", "\\&").replace("%", "\\%")


def main():
    entries = []
    with open(SRC, newline="") as f:
        for r in csv.DictReader(f):
            if r["status"] != "VERIFIED":
                continue
            key = r["bibkey"]
            authors = bib_authors(r["authors"])
            title = esc(r["title"])
            venue = esc(r["venue"])
            year = r["year"]
            ident = r["doi_or_arxiv"]
            fields = [f"  author = {{{authors}}}", f"  title = {{{{{title}}}}}", f"  year = {{{year}}}"]
            if ident.startswith("arXiv:"):
                etype = "misc"
                fields.append(f"  eprint = {{{ident.split(':', 1)[1]}}}")
                fields.append("  archivePrefix = {arXiv}")
                note = venue if venue else "arXiv preprint"
                fields.append(f"  note = {{{{{note}}}}}")
            elif "Proceedings" in venue or "Conference" in venue or "(MSR)" in venue or "(ASE)" in venue or "(SP)" in venue:
                etype = "inproceedings"
                fields.append(f"  booktitle = {{{venue}}}")
                if r["pages"]:
                    fields.append(f"  pages = {{{r['pages']}}}")
                if ident:
                    fields.append(f"  doi = {{{ident}}}")
            else:
                etype = "article"
                fields.append(f"  journal = {{{venue}}}")
                if r["volume"]:
                    fields.append(f"  volume = {{{r['volume']}}}")
                if r["issue"]:
                    fields.append(f"  number = {{{r['issue']}}}")
                if r["pages"]:
                    fields.append(f"  pages = {{{r['pages']}}}")
                if ident:
                    fields.append(f"  doi = {{{ident}}}")
            entries.append(f"@{etype}{{{key},\n" + ",\n".join(fields) + "\n}\n")
    DST.parent.mkdir(exist_ok=True)
    DST.write_text("% auto-generated from REFERENCE_VERIFICATION.csv — do not edit by hand\n\n"
                   + "\n".join(entries))
    print(f"wrote {DST} with {len(entries)} entries")


if __name__ == "__main__":
    main()
