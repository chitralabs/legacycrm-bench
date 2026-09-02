"""Make case_lib importable for all case tests, regardless of how pytest is invoked."""
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent.parent / "03_source_code" / "harness"
if str(_HARNESS) not in sys.path:
    sys.path.insert(0, str(_HARNESS))
