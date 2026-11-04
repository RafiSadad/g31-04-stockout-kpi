# G31-04 Stock-Out Risk Prediction: KPI tables and data flow

Group G31-04, Dataset S1 (item properties, events, category tree, 3 May to 18 Sep 2015).
This repo holds the scripts that build the four KPI tables for the Head of Inventory dashboard,
plus the data flow diagram.

## What is here
| Path | What |
|---|---|
| `outputs/G31-04 KPI Tables.xlsx` | One sheet per KPI, a watch list, and a `Reconcile` sheet that compares every script result with the number written in the proposal |
| `docs/data_flow.png` / `docs/data_flow.mmd` | Data flow diagram (PNG for slides, Mermaid source to edit) |
| `LOG.md` | What each script does, definitions, libraries, how to rerun, what can fail, open findings |
| `scripts/` | `01_extract_properties.py`, `02_explore_snapshots.py`, `03_build_kpis.py`, `config.py` |
| `run_all.sh` | Rebuild everything in one command |

## Quick start
```bash
# put the 4 original CSVs in ./data_raw  (category_tree.csv, events.csv, item_properties_part1.csv, item_properties_part2.csv)
pip install -r requirements.txt
bash run_all.sh            # about 1 minute, needs about 4 GB RAM
```
Raw data (about 1 GB) is not in git. See `LOG.md` for details.
