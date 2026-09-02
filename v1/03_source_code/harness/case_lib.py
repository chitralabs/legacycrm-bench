"""Helpers available to every LegacyCRM-Bench acceptance test.

The harness (and pytest via conftest) prepends this directory to sys.path, so tests do
`import case_lib`. Tests resolve the candidate solution through LCB_SOLUTION_DIR; when it is
unset they fall back to the case's own reference/ directory (ground-truth validation mode).
"""
import csv
import importlib.util
import os
import sys
from pathlib import Path


def case_dir(test_file: str) -> Path:
    """Case root, given a test module's __file__ (tests/ is one level below the case)."""
    return Path(test_file).resolve().parent.parent


def solution_dir(test_file: str) -> Path:
    env = os.environ.get("LCB_SOLUTION_DIR")
    if env:
        return Path(env)
    return case_dir(test_file) / "reference"


def load_solution_module(test_file: str, name: str = "migrated"):
    """Import <solution_dir>/<name>.py under a unique module name. Raises FileNotFoundError
    if the deliverable is absent (tests should call this inside test functions/fixtures)."""
    path = solution_dir(test_file) / f"{name}.py"
    if not path.is_file():
        raise FileNotFoundError(f"deliverable missing: {path}")
    modname = f"lcb_solution_{abs(hash(str(path)))}_{name}"
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    old = sys.modules.get(modname)
    sys.modules[modname] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        if old is not None:
            sys.modules[modname] = old
        else:
            sys.modules.pop(modname, None)
        raise
    return mod


def solution_file(test_file: str, name: str) -> Path:
    """Path to a non-Python deliverable (JSON/SQL/config) in the solution dir."""
    path = solution_dir(test_file) / name
    if not path.is_file():
        raise FileNotFoundError(f"deliverable missing: {path}")
    return path


def legacy_root(test_file: str) -> Path:
    """The case's own legacy/ artifact directory."""
    return case_dir(test_file) / "legacy"


def seed_root(test_file: str) -> Path:
    """Shared seed data (read-only)."""
    d = case_dir(test_file)
    while d.name != "02_benchmark_dataset":
        if d.parent == d:
            raise RuntimeError("cannot locate 02_benchmark_dataset above case dir")
        d = d.parent
    return d / "legacy_system" / "seed_data"


def read_csv(path: Path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def live(rows):
    """Rows not soft-deleted (legacy convention DEL_FLG='Y')."""
    return [r for r in rows if r.get("DEL_FLG", "N") != "Y"]
