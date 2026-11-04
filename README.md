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
| `docs/data_dictionary.md` | Columns we use (raw files and modelling table): type, meaning, example value, why. Made by step 5 |
| `docs/cleaning_log.md` | Rows and columns before and after each cleaning step. Made by step 5 |
| `scripts/` | `01_extract_properties.py`, `02_explore_snapshots.py`, `03_build_kpis.py`, `04_demand_features.py`, `05_docs.py`, helpers `config.py`, `cleanlog.py`, `dictionary_spec.py` |
| `run_all.sh` | Rebuild everything in one command |

## Quick start
```bash
# put the 4 original CSVs in ./data_raw  (category_tree.csv, events.csv, item_properties_part1.csv, item_properties_part2.csv)
pip install -r requirements.txt
bash run_all.sh            # a few minutes, needs about 4 GB RAM
```
On Windows PowerShell without bash, run the scripts one by one:
```powershell
$env:DATA_DIR = "path\to\csvs"
python scripts/01_extract_properties.py; python scripts/02_explore_snapshots.py; python scripts/03_build_kpis.py
python scripts/04_demand_features.py; python scripts/05_docs.py
```
Raw data (about 1 GB) is not in git. See `LOG.md` for details.
