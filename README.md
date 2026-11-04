# G31-04 Stock-Out Risk Prediction: data engineering work of Rafi Sadad Ar Rabbani

Group G31-04, Dataset S1 (Retailrocket-style e-commerce data, 3 May to 18 Sep 2015).
Course INC 362, Introduction to Data Science for Automation Systems.

**Project goal.** Predict whether an in-stock, active item runs out of stock next week, and summarize it as a risk
score per category for a Head of Inventory.

**Scope of this repository.** This repository holds the work of **Rafi Sadad Ar Rabbani (Member 5, Data Engineer,
69540460052)**. It is not the whole group project: the models (Data Scientists), Chapter 3 and the dashboard (Data Analyst)
and the availability-history features (Peeranat, Data Engineer) are done by the other members.

## 1. What Rafi did (tasks from proposal section 2.6)

| Task in the proposal | Result | Where to find it |
|---|---|---|
| This week: prepare the data tables for the 4 KPIs | 4 KPI tables, a watch list, and a check against every number in the proposal | `outputs/G31-04 KPI Tables.xlsx` (sheets `KPI1` to `KPI4`, `Watchlist`, `Reconcile`), `scripts/03_build_kpis.py` |
| This week: data flow diagram, together with Member 2 | Diagram from the raw files to the dashboard | `docs/data_flow.png`, source `docs/data_flow.mmd` |
| Next week: data dictionary of the columns we use | Type, meaning, real example value and reason for every column of the 3 raw files and the modelling table | `docs/data_dictionary.md`, sheet `Data_dictionary`; text in `scripts/dictionary_spec.py`, made by `scripts/05_docs.py` |
| Next week: customer demand features and the reason for each | 9 new features (trend, rates, visitors, last purchase, category demand), using past data only | `scripts/04_demand_features.py`, reasons in `docs/data_dictionary.md` and `LOG.md` section 8 |
| Next week: fix missing category values | "Unknown" category when an item has no category yet, and parent category from `category_tree.csv` ("Unknown" if the category is not in the tree) | `scripts/03_build_kpis.py`, rules in `LOG.md` section 3 |
| Next week: row and column counts in the cleaning log | Rows and columns before and after each of 21 cleaning steps | `docs/cleaning_log.md`, sheet `Cleaning_log`, helper `scripts/cleanlog.py` |
| Every task: record what was done | Definitions, steps, libraries, how to rerun, what can fail, open questions | `LOG.md` |

Commit history: commits by "Rafi Sadad Ar-Rabbani" were made on Rafi's laptop (runs on the real data). Commits by "Claude"
were made with the AI coding assistant Claude Code, working for Rafi and checked by him. Everything was run on the real
data by Rafi on 4 Nov 2026.

## 2. Key results (from the real data, 4 Nov 2026)

- **Reconcile:** 15 of 16 numbers in the proposal match the scripts. The one difference is the KPI 3 minimum
  (proposal 29%, script 21.9% on 10 May). See `LOG.md` section 4.
- **Modelling table:** 283,849 rows (one item in one week), 29,502 stock-outs (10.4%), 26 columns after the demand features.
- **Cleaning:** 20,275,902 property rows reduced to 2,291,853 (only `available` and `categoryid`); 417,053 items x 18 weekly snapshots;
  883,701 item-week cells without a category yet, filled as "Unknown" (29,358 modelling rows, 90% of them in the first 5 weeks).
- **Category tree:** 30 of the 1,242 category ids in the item data are not in the tree (matches the proposal). None of them is in the modelling table.

## 3. Where the data is (the CSVs are NOT on GitHub)

The raw CSVs are large (item_properties about 461 MB and 389 MB, events about 90 MB) and are **not uploaded to GitHub**.
GitHub only holds the code and the small results (the largest file in the repository is the diagram, about 0.4 MB).
GitHub also refuses files above 100 MB. The scripts read the CSVs **from your own disk**.

On Rafi's laptop the CSVs are in the folder one level above the repository:

```
Project Based\
  category_tree.csv
  events.csv
  item_properties_part1.csv
  item_properties_part2.csv
  g31-04-stockout-kpi\        <- this repository
```

The environment variable `DATA_DIR` tells the scripts where the CSVs are. `..` means "the folder above".
That the real files were read can be seen in the cleaning log: 10,999,999 + 9,275,903 property rows and 2,756,101 events.
Other group members need their own copy of the 4 CSVs (course zip `item_properties_part1.zip`).

Files made during a run but not uploaded: `work/` (intermediate tables, for example the modelling table
`work/modelling_table_features.csv.gz`). They are rebuilt by the scripts.

## 4. How to run

Needs Python 3.12 or newer, about 4 GB RAM, a few minutes.

**Windows PowerShell** (CSVs in the folder above the repository):
```powershell
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File run_all.ps1
```
If the CSVs are somewhere else: `$env:DATA_DIR = "C:\path\to\csvs"` before the second line.

**Linux or macOS, or Git Bash**:
```bash
DATA_DIR=.. bash run_all.sh
```

After a run, open `outputs/G31-04 KPI Tables.xlsx`, sheet `Reconcile` (expect 15 OK and 1 known DIFF).
Do not stop step 4 with Ctrl+C: it writes a large file and the file is left broken (just run it again).

## 5. The pipeline

| Step | Script | What it does | Output |
|---|---|---|---|
| 1 | `01_extract_properties.py` | Reads the 2 big property files in chunks, keeps only `available` and `categoryid` | `work/item_props_small.csv.gz` |
| 2 | `02_explore_snapshots.py` | Checks the 18 snapshot dates and basic counts (prints only) | none |
| 3 | `03_build_kpis.py` | Weekly item table: status (forward fill), category ("Unknown", parent), demand, active flag, label; KPI tables | `work/modelling_table.csv.gz`, xlsx |
| 4 | `04_demand_features.py` | Adds the 9 demand features | `work/modelling_table_features.csv.gz` |
| 5 | `05_docs.py` | Writes the data dictionary and the cleaning log | `docs/*.md`, 2 xlsx sheets |

Helpers: `config.py` (folders, Unknown code), `cleanlog.py` (cleaning log), `dictionary_spec.py` (dictionary text).
Libraries: pandas, numpy, openpyxl. Full details: `LOG.md`.

## 6. Open points for the group

- **To the Data Analyst (Sirawich):** KPI 3 range in the proposal (29 to 49%) vs script (21.9 to 48.6%); 1,180 categories in the proposal vs 1,242 in the data.
- **To Peeranat (Data Engineer):** check the data flow diagram; decide whether a category may be filled backwards from later weeks
  (would remove most "Unknown" rows, but uses a later record); availability-history features are his task.
- **Not checked yet:** the meaning of `available = 0` (proposal 2.5).
