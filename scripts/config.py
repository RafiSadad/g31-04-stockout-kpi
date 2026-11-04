"""Shared paths. Override DATA_DIR / WORK_DIR / OUT_DIR / DOCS_DIR with environment variables."""
import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("DATA_DIR", "data_raw"))   # the 4 original CSVs
WORK_DIR = Path(os.environ.get("WORK_DIR", "work"))       # intermediate files (git-ignored)
OUT_DIR = Path(os.environ.get("OUT_DIR", "outputs"))      # final tables and figures
DOCS_DIR = Path(os.environ.get("DOCS_DIR", "docs"))       # data dictionary and cleaning log (markdown)
for d in (WORK_DIR, OUT_DIR, DOCS_DIR):
    d.mkdir(parents=True, exist_ok=True)

UNKNOWN_CAT = -1   # code for "Unknown" category (no categoryid known at or before the snapshot)
