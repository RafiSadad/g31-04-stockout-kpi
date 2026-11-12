#!/usr/bin/env bash
# Rebuild everything from the 4 original CSVs.
# Usage: DATA_DIR=/path/to/csvs bash run_all.sh      (default DATA_DIR=./data_raw)
set -euo pipefail
cd "$(dirname "$0")"
pip install -q -r requirements.txt
python scripts/01_extract_raw.py
python scripts/02_explore_snapshots.py
python scripts/03_build_kpis.py
python scripts/04_demand_features.py
python scripts/05_docs.py
python scripts/06_export_compare.py
python scripts/07_charts.py
# optional: mmdc -i docs/data_flow.mmd -o docs/data_flow.png -w 2400 -b white -s 2
