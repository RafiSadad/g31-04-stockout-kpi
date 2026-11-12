# LOG: how the KPI tables were built

Written 4 Nov 2026 for group G31-04. Goal: make the 4 KPI tables and the data flow diagram so the group can
reuse them and rerun them if something breaks.

## 1. Environment
- Python 3.12, pandas 3.0.5, numpy, openpyxl (see `requirements.txt`). Mermaid CLI (`mmdc`) only for the diagram.
- Run time about 20 s for step 1 and about 20 s for step 3 on 2 CPU and 7 GB RAM.
- Input: the 4 CSVs from the course zip (`category_tree.csv`, `events.csv`, `item_properties_part1.csv`, `item_properties_part2.csv`).
  Put them in `data_raw/` or set `DATA_DIR`. `work/` (intermediate) and `outputs/` (final) can be changed with `WORK_DIR`, `OUT_DIR`.
- All timestamps in the files are Unix milliseconds. The script treats them as UTC. Snapshot "dates" are the UTC dates.

## 2. Steps
| Step | Script | Input | Output | What it does |
|---|---|---|---|---|
| 1 | `01_extract_raw.py` (was `01_extract_properties.py`) | item_properties part 1 and 2 (20,275,902 rows), events | `work/item_props_small.csv.gz` (2,291,853 rows), `work/events_clean.csv.gz` | Reads in chunks of 2M rows and keeps only `property` = `available` (1,503,639 rows) and `categoryid` (788,214 rows). Removes exact duplicate events (since 12 Nov 2026, section 12). Starts a new cleaning log. |
| 2 | `02_explore_snapshots.py` | step 1 outputs | printed only | Finds the snapshot dates and checks coverage. Confirms 18 dates, 21 Jun missing, 417,053 items, 1,407,580 visitors. |
| 3 | `03_build_kpis.py` | step 1 output, events | `work/modelling_table.csv.gz`, `work/item_week.csv.gz`, `outputs/G31-04 KPI Tables.xlsx` | Builds the weekly item table and all KPI tables (below). Fills missing category with "Unknown". `item_week` = all active items per snapshot (category, demand), input for step 4. |
| 4 | `04_demand_features.py` | step 3 and step 1 output, events | `work/modelling_table_features.csv.gz` | Adds 9 demand features to the modelling table (section 8). Same rows, more columns. |
| 5 | `05_docs.py` | outputs of steps 1 to 4, small parts of the raw CSVs | `docs/data_dictionary.md`, `docs/cleaning_log.md`, sheets `Data_dictionary` and `Cleaning_log` in the xlsx | Writes the data dictionary (text from `scripts/dictionary_spec.py`, example values from the data) and the cleaning log. Does not touch the other sheets. |
| 6 | `06_export_compare.py` | step 4 output, cleaning log, xlsx | `outputs/G31-04_Progress1_CleanedData.csv`, `outputs/compare_progress1.csv` | Exports the cleaned modelling table as CSV and compares our counts with the Progress 1 slides (section 12). |
| 7 | `docs/data_flow.mmd` | none | `docs/data_flow.png` | `mmdc -i docs/data_flow.mmd -o docs/data_flow.png -w 2400 -b white -s 2` |

## 3. Definitions used in step 3 (from the proposal, sections 1.2 and 2.2)
- **Snapshot**: one of the 18 weekly dates where `available` was recorded (10 May to 13 Sep 2015, 21 Jun missing).
- **Status of an item at a snapshot**: the last known `available` value at or before that snapshot (forward fill across snapshots). 1 = in stock, 0 = out of stock. This reading of `available` is still an assumption (proposal 2.1).
- **Active**: at least one event (view, addtocart, transaction) in the 7 days up to and including the snapshot.
- **Demand**: views + add-to-carts in the same 7 days. Windows of 28 days are also stored (`*_4w` columns).
- **Category**: last known `categoryid` at or before the snapshot. If there is none, the category is **"Unknown"** (code `cat = -1`, flag `cat_missing = 1`).
  This happens when the item never has a `categoryid`, or when its first `categoryid` is recorded after the snapshot. We do not fill backwards
  from later records, because that would use information from the future. (Added 4 Nov 2026, see section 8.)
- **Parent category**: `parentid` of the category in `category_tree.csv`. A top-level category (25 have no parent) is its own parent.
  If the category is "Unknown" or not in the tree, the parent is "Unknown" (`parent_cat = -1`) and `cat_in_tree = 0`. This follows proposal 2.5
  ("25 categories have no parent, 30 category IDs are not in the tree ... We use an Unknown category"). (Added 4 Nov 2026, see section 9.)
- **Label**: 1 if the item is out of stock at the snapshot exactly 7 days later. Weeks whose next snapshot is not 7 days away are skipped (14 Jun, because 21 Jun is missing; 13 Sep, because it is the last date). This leaves 16 prediction weeks: 10 train (10 May to 26 Jul), 3 validate (2 to 16 Aug), 3 test (23 Aug to 6 Sep).
- **Eligible rows (modelling table)**: items in stock and active at the snapshot.
- **KPI 1**: among active items with a known status, share with status 0.
- **KPI 2**: for each prediction week, among eligible rows, per category: eligible items, observed stock-outs, observed stock-out rate, and the demand-weighted rate = 100 x sum(demand x outcome) / sum(demand). Only categories with at least 20 eligible items are ranked. "Unknown" is never ranked and does not count in the eligible or high-risk numbers, because it is not a real category the Head of Inventory can act on. It is shown as its own row (tier "Unknown category (not ranked)") and its item count per week is in the column `unknown_category_items` of `KPI2_by_week`. High = top 10% by the observed stock-out rate (rounded count), Medium = next 20%, Low = rest. The model probability will replace the observed outcome once a model exists. The sheet `KPI2_categories_latest` is the week 6 to 13 Sep.
- **KPI 3**: share of views + add-to-carts in the 7 days that went to items with status 0 at the snapshot. Items with no known status stay in the denominator only.
- **KPI 4 (rule baseline, no model yet)**: predict stock-out if the item changed status in the last 4 snapshot steps. Confusion counts, recall, precision, F1 per week and pooled per split. PR-AUC is not computed because a yes/no rule has no probability. It will be added with the models.
- **Watchlist**: top 50 in-stock active items on 13 Sep with at least one status change in the last 4 weeks, sorted by 7-day demand. Predicted probability column is empty on purpose.

## 4. Check against the proposal (sheet `Reconcile`)
15 of 16 numbers match: KPI 1 (58%, 59%, 43 to 60%), 220 eligible categories, 22 high-risk, KPI 3 on 13 Sep (43.5% vs 43%), KPI 3 upper bound (48.6% vs 49%),
283,849 rows, 29,502 stock-outs (10.4%), rule recall 0.42, precision 0.24, F1 0.30 and 11.3% stock-outs on the test weeks.

**One difference to settle with the Data Analyst.** The proposal says KPI 3 ranges from 29% to 49%. The script gives 21.9% (10 May) to 48.6% (2 Aug).
The first two snapshots (10 and 17 May, 21.9% and 24.9%) are the low ones, and the next lowest is 30.2% (24 May). Either the proposal used another rule for the early weeks, or the sentence should say 22 to 49%.
Also note: 43.5% on 13 Sep is written as 43% in the proposal, which looks like truncation, not rounding.

## 5. Things to remember
- The modelling table has the stock-out label only for in-stock active items, so it is built for classification, not for KPI 1 or KPI 3 (those use all active items or all demand).
- `category_tree.csv` is used since 4 Nov 2026 for `parent_cat` (step 3). KPI 2 is still computed at category level, not parent level.
- Before 4 Nov 2026 rows without a category were silently dropped by `groupby` in the per-category sheets (KPI 2 latest, KPI 3 by category) and had an empty category in the watch list. They now show as "Unknown". The KPI numbers themselves did not change (tested, section 8).
- `demand_4w`, `demand_prev3w_avg` and `demand_trend` are less reliable for the first 3 snapshots (10, 17, 24 May): the 28-day window starts before the data (3 May), so the earlier weeks look lower than they were and the trend looks higher.
- Early snapshots have less history, so `changes_4w` uses fewer than 4 steps for the first 4 dates.
- KPI 2 ranks categories by the observed stock-out rate (as in the proposal mockup). The demand-weighted column is next to it for comparison, and is what the model risk score will use.
- Dates in the xlsx are text (`YYYY-MM-DD`) on purpose so Excel does not reformat them.

## 6. If something fails
| Symptom | Cause and fix |
|---|---|
| `FileNotFoundError` for a CSV | Files are not in `data_raw/`. Set `DATA_DIR`. |
| `MemoryError` or the process is killed in step 1 | Lower `chunksize` in `01_extract_properties.py` (currently 2,000,000). Step 3 needs about 4 GB. |
| `No such file work/item_props_small.csv.gz` | Run step 1 first (or `run_all.sh`). |
| Different numbers from the table in section 4 | Check the CSV versions (row counts must be 20,275,902 properties and 2,756,101 events), and that forward fill and the 7-day window were not changed. |
| Excel file locked | Close the xlsx in Excel, then rerun step 3. |
| Step 4 says `No such file work/item_week.csv.gz` | Rerun step 3 (the file is new since 4 Nov 2026). |
| Step 4 `AssertionError: row count changed` or `duplicate item-week rows` | A merge key is not unique. Check that step 3 and step 4 were run on the same data. |
| Step 5 `dictionary_spec.py is out of date` | A column was added or removed in the modelling table. Add or remove it in `scripts/dictionary_spec.py`, then rerun step 5. |
| Step 5 `Permission denied` or `BadZipFile` on the xlsx | The xlsx is open in Excel or was not written by step 3. Close it and rerun steps 3 and 5. |
| `cleaning_log.csv` has old rows | Each script replaces only its own rows. Delete `work/cleaning_log.csv` and run `run_all.sh` for a clean log. |

## 7. Not done
- No model is trained. KPI 4 uses the rule only.
- `available = 0` meaning is still unverified.
- Open question for the group: all 883,701 "Unknown" cells are items whose `categoryid` is only recorded after the snapshot (none is an item without any category). If category is a fixed attribute, filling it backwards would remove "Unknown" completely. We do not do this now, because it uses a later record (section 8).
- The data flow diagram is still a draft for Peeranat to check against the final cleaning pipeline (it now shows steps 4 and 5, "Unknown" and the parent category).
- Proposal 2.1 says 1,180 categories, but step 2 counts 1,242 distinct `categoryid` values in item_properties. The proposal does not say how 1,180 was counted (maybe a subset of items). To settle with the Data Analyst.

## 8. Task 4 Nov 2026: data dictionary, demand features, Unknown category, cleaning log (Rafi)
**What was done**
- `scripts/cleanlog.py` (new): small helper. Each script writes one row per cleaning step to `work/cleaning_log.csv`: script, step, action, table, rows and columns before and after, rows changed, note. A rerun replaces the rows of that script only.
- Step 1 now logs the raw row counts of both files and the property filter.
- Step 3 now logs: loading, duplicate removal for `available` and `categoryid`, the pivot to the item x snapshot matrix, forward fill (empty cells before and after), the "Unknown" fill (how many cells, split into "never has a category" and "category only known later"), the event type filter, dropping weeks without a label, and the eligibility filter.
- Step 3, missing category: filled with "Unknown" (`cat = -1`) plus a flag `cat_missing`. Definition added in section 3. In the xlsx the code is written as the word `Unknown`.
- Step 4 (new): demand features. Step 5 (new): data dictionary and cleaning log. `run_all.sh` runs both.
- `config.py`: `UNKNOWN_CAT = -1` and `DOCS_DIR` (default `docs`).
- Libraries: pandas, numpy, openpyxl only (no new ones).

**Demand features (step 4)** All use events at or before the snapshot time t only. Full meaning and example values in `docs/data_dictionary.md`.

| Feature | Formula | Why |
|---|---|---|
| `demand_4w` | views_4w + atc_4w | Monthly demand level, smoother than one week. |
| `demand_prev3w_avg` | (demand_4w - demand_1w) / 3 | Normal weekly demand before the last week. |
| `demand_trend` | (demand_1w + 1) / (demand_prev3w_avg + 1) | Rising demand can empty stock before it is refilled. |
| `atc_rate_1w` | atc_1w / views_1w (0 if no views) | Buying intent per view. |
| `buy_rate_4w` | tx_4w / views_4w (0 if no views) | How well views turn into sales. |
| `visitors_1w` | distinct visitors with view or add-to-cart in 7 days | Broad demand vs one visitor viewing many times. |
| `days_since_last_tx` | days from last purchase at or before t (empty if none) | Items that sold recently are more likely to run out. |
| `cat_demand_1w` | sum of demand_1w of all active items in the category (empty for Unknown) | How busy the category is. |
| `item_share_of_cat_demand` | demand_1w / cat_demand_1w | Main seller or small item within its category. |

The existing columns of step 3 (`views_*`, `atc_*`, `tx_*`, `demand_1w`, `changes_4w`) are kept and their reasons are in the dictionary.

**How it was checked.** First on a synthetic test set with the same columns (made only for testing, not saved in the repo): the old and the new step 3
gave the same KPI values; the only additions were the "Unknown" rows and the column `unknown_category_items`.
Then Rafi ran steps 1 to 5 on the real data (Windows, Python 3.13, pandas 3.0.5, 4 Nov 2026). Results:
- `Reconcile`: 15 OK and the known DIFF (KPI3 min 21.9 vs 29, section 4). 220 eligible and 22 high-risk categories did not change.
- Raw counts as before: 20,275,902 property rows (10,999,999 + 9,275,903), 2,756,101 events, 2,291,853 rows kept in step 1.
- No duplicate (itemid, timestamp) rows for `available` or `categoryid` (0 rows dropped).
- Status matrix 417,053 items x 18 snapshots. Forward fill: empty cells 6,003,315 -> 799,066.
- Category: 202,531 items have at least one snapshot without a category. 883,701 cells filled with "Unknown", all of them items whose category is only recorded later.
- Modelling table 283,849 rows (as before), of which 29,358 rows (10.3%) have category "Unknown". Most of them are early: 26,361 (90%) are in the first 5 weeks (7,600 on 10 May, 6,821 on 17 May, 5,665 on 24 May, 3,365 on 31 May, 2,910 on 7 Jun), and from 28 Jun on it is 140 to 451 per week (column `unknown_category_items` in `KPI2_by_week`). So `categoryid` seems to be recorded later than `available` for many items, and "Unknown" falls mostly in the train split.
  On 13 Sep no Unknown item has demand, so `KPI3_by_category` has no Unknown row that day. Step 4: 283,849 x 15 -> 283,849 x 24.
- Features: `days_since_last_tx` is empty in 230,343 rows (81%, no purchase before t). `cat_demand_1w` and `item_share_of_cat_demand` are empty in the 29,358 Unknown rows.
  `atc_rate_1w` reaches 26 and `buy_rate_4w` reaches 3 (add-to-carts or purchases without a view in the window). Consider capping them before a linear model.

**How to rerun**: `bash run_all.sh`, or only the new parts: `python scripts/03_build_kpis.py && python scripts/04_demand_features.py && python scripts/05_docs.py`.
Then open the `Reconcile` sheet (expect 15 OK and the known KPI3 min DIFF) and `Cleaning_log`.

**What can fail**: see section 6 (last four rows). Also: step 4 reads `events.csv` with `visitorid`, which needs a bit more RAM than step 3 (one more integer column).

## 9. Task 4 Nov 2026 (second part): parent category (Rafi)
**Why.** Proposal 2.2 lists "category and parent category" as features, and proposal 2.5 says category IDs that are not in the tree get an "Unknown" category.
The first part (section 8) only handled items with no category at all.

**What was done**
- Step 3 reads `category_tree.csv` (1,669 rows, small, read whole) and adds two columns to the modelling table: `parent_cat` and `cat_in_tree` (rule in section 3).
  The modelling table now has 17 columns (with `itemid`), the feature table 26.
- Two new rows in the cleaning log: "load category tree" and "map category to parent category". The second note gives how many `categoryid` values
  of item_properties are not in the tree, how many modelling rows that affects, and how many rows have a top-level category.
- `dictionary_spec.py`: `category_tree` columns are now "yes (step 3)", and `parent_cat` and `cat_in_tree` are described.
- `docs/data_flow.mmd` and `docs/data_flow.png`: category tree is now a solid input, and steps 4 and 5 and the "Unknown" fill are shown. PNG rendered with mermaid-cli 11.4.2 (`mmdc`, command in section 2).
- Checked on the synthetic test set with the real `category_tree.csv`: all KPI sheets and Reconcile are identical to the run before this change. No KPI uses the parent yet.

**How to rerun.** `category_tree.csv` must be in `DATA_DIR` (it already is in the course zip). Then steps 3, 4 and 5 (steps 1 and 2 do not change):
`python scripts/03_build_kpis.py`, `python scripts/04_demand_features.py`, `python scripts/05_docs.py`. Check Reconcile (15 OK + the known DIFF).

**Result on the real data (Rafi, 4 Nov 2026).** Reconcile: 15 OK and the known KPI3 min DIFF. 30 of the 1,242 `categoryid` values in item_properties
are not in `category_tree.csv`, which matches proposal 2.5. None of them appears in the modelling table (0 rows), so in practice `cat_in_tree = 0` only
for the 29,358 Unknown rows. 5 modelling rows have a top-level category (own parent). Modelling table 283,849 x 17, feature table 283,849 x 26.

**What can fail.** `FileNotFoundError: category_tree.csv` if the file is not in `DATA_DIR`. Step 4 writes a large gzip file and can take a few minutes;
do not stop it with Ctrl+C, or `modelling_table_features.csv.gz` is left half written (then rerun step 4).

## 10. README and Windows runner (4 Nov 2026)
- `README.md` rewritten: scope is Rafi's Data Engineer work, a table of each proposal task with the file that holds the result, key results,
  where the CSVs are (not on GitHub, read from the local disk through `DATA_DIR`), how to run, open points.
- `run_all.ps1` (new): runs steps 1 to 5 on Windows PowerShell. Default `DATA_DIR` is `..` (the folder above the repository, where Rafi keeps the CSVs).
  It stops with a clear message if one of the 4 CSVs is missing, or if a step fails.
  Rerun: `powershell -ExecutionPolicy Bypass -File run_all.ps1`. Tested by Rafi on Windows on 4 Nov 2026: all 5 steps ran, Reconcile 15 OK and the known KPI3 min DIFF, same numbers as the run before. `run_all.sh` does the same with bash.

## 11. Dataset overview picture (5 Nov 2026)
- `docs/dataset_schema.png`: one slide-sized picture (1600 x 900, rendered at 2x) of the 3 source files, their row counts, key columns,
  join keys (`itemid`, `categoryid`) and the modelling table. Every number comes from the script outputs of 4 Nov (sections 8 and 9).
- Source: `docs/dataset_schema.html` (plain HTML and CSS). To change it, edit the HTML and take a new screenshot, for example with
  Playwright: open the file at 1600 x 900 and save a PNG. If the scripts change any count, update the HTML by hand.

## 12. Clean version run in Google Colab (12 Nov 2026)
**Why.** At Progress 1 the lecturer asked why the numbers were not consistent (20 million rows, then 6 million). Two things were found:
1. The chain of counts was right but was not explained. Item properties are in a long format (one row = one property value of one item at
   one time; 1,104 different properties), so the counts go 20,275,902 -> 2,291,853 (2 properties) -> first record and changes only
   -> one row per item and week (417,053 items x 18 snapshots minus the weeks before the first status). The number of rows goes up in the
   last step because the format changes, not because data is added. Step 3 now logs both counts, so the chain is in the cleaning log.
2. The group had two pipelines. The Progress 1 slides come from another pipeline (`clean_data.py`, `build_features.py`, not in this repository),
   with slightly different counts (for example 282,708 vs 283,849 modelling rows). It removes 460 duplicate events and uses site time (UTC+3).

**What was done**
- `01_extract_raw.py` (renamed from `01_extract_properties.py`) also removes exact duplicate events (all 5 columns equal) and writes
  `work/events_clean.csv.gz`. Steps 2, 3 and 4 read the cleaned events. Step 1 also deletes the old cleaning log, so every full run has one clean log.
- `03_build_kpis.py`: two new cleaning log rows, "count first record and each status change (check only)" and "item-weeks with a known status".
- `03_build_kpis.py`, Reconcile: **bug fixed**. The old check used one tolerance (0.51) for all rows, so a recall of 0.38 would have shown OK
  against 0.42. Now each row has its own tolerance, shown in the new column `tolerance`: half of the last digit written in the proposal
  (58 -> 0.5, 10.4 -> 0.05, 0.42 -> 0.005); counts must be equal. On the 4 Nov run all rows were inside the new tolerances too.
- `06_export_compare.py` (new): writes `outputs/G31-04_Progress1_CleanedData.csv` (submission file, not in git) and `outputs/compare_progress1.csv`
  (our counts next to the Progress 1 slide numbers, "same" or "DIFF"). The slide numbers are typed from the slide PDF; ours come from the run.
- `notebooks/G31-04_DataPrep_Colab.ipynb` (new): clones the repository, copies the 4 CSVs from Google Drive into `data_raw/` (or extracts them
  from a zip), installs the libraries, runs steps 1 to 6, shows the cleaning log, Reconcile, the slide comparison, the feature summary and the
  diagrams, and saves the results to Google Drive. Optional last cell pushes the docs and workbook to GitHub with a `GITHUB_TOKEN` Colab secret.
- `data_raw/README.md` (new): the folder for the raw CSVs is now in the repository (the CSVs stay ignored by git). `run_all.ps1` uses `data_raw/`
  when it holds the files, else the folder above. `outputs/*.csv` is ignored by git.
- Timestamps stay in UTC (section 1). Site time (UTC+3) is not used; this is one known reason for differences with the other pipeline.
- Tested on the synthetic test set only (37 duplicate events added and removed, all cells of the notebook ran). Not yet run on the real data.

**How to rerun.** In Colab: open the notebook, set `RAW_DRIVE_DIR`, *Runtime > Run all*. Locally: `run_all.ps1` or `run_all.sh`.

**What can fail.** `FileNotFoundError ... Check RAW_DRIVE_DIR`: the Drive folder is not in *My Drive* (add a shortcut) or the path is wrong.
`git clone` asks for a password: the repository is private, add the `GITHUB_TOKEN` Colab secret. Colab disconnects after long idle time:
run all again (about 5 to 10 minutes). Expect small changes in demand-based numbers after the duplicate removal; row counts should not change,
because a duplicate event never makes an item active on its own.
