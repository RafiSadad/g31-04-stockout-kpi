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
Other group members need their own copy of the 4 CSVs. Download them from the group Google Drive folder:
https://drive.google.com/drive/folders/1-_Qns7aF7vowcg9gIa5i7x6i3qTCtGDm
Unzip and put the 4 CSVs in the folder above the repository (as in the picture above), not inside it.

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

## 6. Messages for the group

**Start here (5 minutes):** look at the [data flow diagram](docs/data_flow.png), then the [data dictionary](docs/data_dictionary.md),
then the [cleaning log](docs/cleaning_log.md). All numbers come from the real data, run on 4 Nov 2026.
The Excel file with every table is [outputs/G31-04 KPI Tables.xlsx](outputs/G31-04%20KPI%20Tables.xlsx) (download it, GitHub cannot show xlsx).

### To Sirawich (Data Analyst, Chapter 3)
Numbers for Chapter 3 (Data Preparation), ready to copy:
- Cleaning steps with rows and columns before and after: [docs/cleaning_log.md](docs/cleaning_log.md) (21 steps). Short version is in [section 2](#2-key-results-from-the-real-data-4-nov-2026).
- Columns, meaning and reason for each feature: [docs/data_dictionary.md](docs/data_dictionary.md).
- Missing values: "Unknown" category for 883,701 item-week cells without a category yet (29,358 modelling rows);
  30 of 1,242 category ids are not in the tree (matches proposal 2.5). Rules: [LOG.md section 3](LOG.md#3-definitions-used-in-step-3-from-the-proposal-sections-12-and-22).

**Please check 2 numbers in the proposal** (details in [LOG.md section 4](LOG.md#4-check-against-the-proposal-sheet-reconcile)):
1. KPI 3 range: proposal says 29 to 49%, the script gives 21.9% (10 May) to 48.6% (2 Aug). Without the first two weeks the minimum is 30.2%.
   Either change the text to "22 to 49%" or explain the rule used for the early weeks.
2. Number of categories: proposal 2.1 says 1,180, the data has 1,242 distinct category ids in item_properties. How was 1,180 counted?

### To Peeranat (Data Engineer)
1. Please check the [data flow diagram](docs/data_flow.png) (source to edit: [docs/data_flow.mmd](docs/data_flow.mmd)) against your cleaning pipeline. You own the final version.
2. **Decision needed:** an item's category is often recorded only some weeks after its stock status. 90% of the 29,358 "Unknown" rows are in the
   first 5 weeks. We could fill the category backwards from the first known value. This removes most "Unknown" rows, but uses a record from
   after the snapshot. It is only safe if an item's category does not change. Please decide together with the Data Scientists.
3. Your features (weeks since last status change, number of changes) can be added to the same table. Only `changes_4w` exists now (used by the KPI 4 rule).
4. The meaning of `available = 0` (proposal 2.5) is still to be confirmed.

### To the Data Scientists (EDA part 1 and 2, models)
- **Table to use:** `work/modelling_table_features.csv.gz` (283,849 rows x 26 columns, one row = one item in one week). It is not on GitHub;
  make it on your laptop with `run_all.ps1` ([how to run](#4-how-to-run)). Column meanings: [data dictionary](docs/data_dictionary.md).
- **Target:** `y_next_out` (1 = out of stock at the next weekly snapshot). 29,502 positives (10.4%).
- **Time split:** use the column `snapshot`. Train 2015-05-10 to 2015-07-26, validate 2015-08-02 to 2015-08-16, test 2015-08-23 to 2015-09-06.
- **Do not use as features:** `itemid`, `snapshot`, `y_next_out`, and `state` and `active` (always 1 and true in this table).
- **Leakage check (EDA part 2):** every feature uses only data at or before the snapshot time t. The label comes from the snapshot at t + 7 days.
  Details: [LOG.md section 8](LOG.md#8-task-4-nov-2026-data-dictionary-demand-features-unknown-category-cleaning-log-rafi).
- **Things to handle before training:**
  - `days_since_last_tx` is empty in 230,343 rows (81%, no purchase before t). Fill it (for example with a large number) and add a flag.
  - `cat_demand_1w` and `item_share_of_cat_demand` are empty for the 29,358 "Unknown" category rows.
  - `atc_rate_1w` (max 26) and `buy_rate_4w` (max 3) have a few very large values. Cap them for Logistic Regression.
  - `cat` and `parent_cat` are codes, not quantities. -1 means "Unknown". Treat them as categories, not as numbers.
  - 4-week features are partial in the first 3 weeks (data starts on 3 May).

### Questions about this repository
Ask Rafi (Member 5). Full log of what was done and how to rerun: [LOG.md](LOG.md).
