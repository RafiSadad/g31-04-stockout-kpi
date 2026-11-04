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
| 1 | `01_extract_properties.py` | item_properties part 1 and 2 (20,275,902 rows) | `work/item_props_small.csv.gz` (2,291,853 rows) | Reads in chunks of 2M rows and keeps only `property` = `available` (1,503,639 rows) and `categoryid` (788,214 rows). Needed because the full files do not fit comfortably in memory as strings. |
| 2 | `02_explore_snapshots.py` | step 1 output, events | printed only | Finds the snapshot dates and checks coverage. Confirms 18 dates, 21 Jun missing, 417,053 items, 1,407,580 visitors. |
| 3 | `03_build_kpis.py` | step 1 output, events | `work/modelling_table.csv.gz`, `outputs/G31-04 KPI Tables.xlsx` | Builds the weekly item table and all KPI tables (below). |
| 4 | `docs/data_flow.mmd` | none | `docs/data_flow.png` | `mmdc -i docs/data_flow.mmd -o docs/data_flow.png -w 2400 -b white -s 2` |

## 3. Definitions used in step 3 (from the proposal, sections 1.2 and 2.2)
- **Snapshot**: one of the 18 weekly dates where `available` was recorded (10 May to 13 Sep 2015, 21 Jun missing).
- **Status of an item at a snapshot**: the last known `available` value at or before that snapshot (forward fill across snapshots). 1 = in stock, 0 = out of stock. This reading of `available` is still an assumption (proposal 2.1).
- **Active**: at least one event (view, addtocart, transaction) in the 7 days up to and including the snapshot.
- **Demand**: views + add-to-carts in the same 7 days. Windows of 28 days are also stored (`*_4w` columns).
- **Category**: last known `categoryid` at or before the snapshot.
- **Label**: 1 if the item is out of stock at the snapshot exactly 7 days later. Weeks whose next snapshot is not 7 days away are skipped (14 Jun, because 21 Jun is missing; 13 Sep, because it is the last date). This leaves 16 prediction weeks: 10 train (10 May to 26 Jul), 3 validate (2 to 16 Aug), 3 test (23 Aug to 6 Sep).
- **Eligible rows (modelling table)**: items in stock and active at the snapshot.
- **KPI 1**: among active items with a known status, share with status 0.
- **KPI 2**: for each prediction week, among eligible rows, per category: eligible items, observed stock-outs, observed stock-out rate, and the demand-weighted rate = 100 x sum(demand x outcome) / sum(demand). Only categories with at least 20 eligible items are ranked. High = top 10% by the observed stock-out rate (rounded count), Medium = next 20%, Low = rest. The model probability will replace the observed outcome once a model exists. The sheet `KPI2_categories_latest` is the week 6 to 13 Sep.
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
- `category_tree.csv` is not used yet. Parent category is a model feature for later.
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

## 7. Not done
- No model is trained. KPI 4 uses the rule only.
- The data flow diagram is a draft. The Data Engineer who owns the final version (Peeranat) should correct it against the real cleaning pipeline.
- `available = 0` meaning is still unverified.
