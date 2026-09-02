"""AUD-01 reference solution: audit_config.cfg parser.

Parses the legacy audited-column configuration (SYSTEM_OVERVIEW.md §8) from injected text:
line-oriented, '#' comments, blank lines ignored, 'AUDIT <TABLE> <COLUMN>' declarations.
"""


def audited_columns(cfg_text):
    out = {}
    for raw in cfg_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) == 3 and parts[0] == "AUDIT":
            _, table, column = parts
            out.setdefault(table, set()).add(column)
    return out
