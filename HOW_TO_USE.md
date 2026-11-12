# How to use this repository

Group G31-04, Dataset S1. This guide is for every group member. You do not need to install anything if you use Google Colab.

**The one rule:** every number and chart in our slides and report must come from these scripts. Never type or change a
number by hand. If something must change, change the script, run everything again, and use the new outputs.

## 1. Run everything in Google Colab (recommended)

### 1.1 Before the first run (once)
1. Open the group Google Drive folder with the raw data:
   https://drive.google.com/drive/folders/1-_Qns7aF7vowcg9gIa5i7x6i3qTCtGDm
2. Right-click the folder and choose **Organize > Add shortcut** (or **Add shortcut to Drive**), then pick **My Drive**.
   Colab can only see files that are in your own Drive.
3. Remember the folder name as it appears in My Drive, for example `G31-04`.

### 1.2 Open the notebook
- If the repository is public, open this link:
  https://colab.research.google.com/github/RafiSadad/g31-04-stockout-kpi/blob/main/notebooks/G31-04_DataPrep_Colab.ipynb
- If the repository is private: download `notebooks/G31-04_DataPrep_Colab.ipynb` from GitHub, then in Colab choose
  **File > Upload notebook**. Also add a GitHub token as a Colab secret (see section 4).

### 1.3 Run it
1. In **cell 1 (Settings)**, set `RAW_DRIVE_DIR` to your folder, for example `/content/drive/MyDrive/G31-04`.
   The folder may hold the 4 CSV files or a zip with them. Sub-folders are searched too.
2. Choose **Runtime > Run all**.
3. Allow Colab to access your Google Drive when it asks.
4. Wait about 5 to 10 minutes. Each step prints what it did. If a step fails, the notebook stops and shows the error (see section 5).

### 1.4 What the notebook does
| Cell | What happens |
|---|---|
| 1. Settings | Paths for the raw data and for the results |
| 2. Drive and GitHub | Connects Google Drive and clones (or updates) this repository |
| 3. Raw files | Copies the 4 CSVs into `data_raw/` inside the repository (extracts them from a zip if needed) |
| 4. Libraries | Installs `requirements.txt` and prints the versions used |
| Steps 1 to 7 | Runs the numbered scripts in `scripts/` (table in section 3) |
| Results | Shows the cleaning log, Reconcile, the comparison with the Progress 1 slides, the feature summary, the diagrams and all charts |
| Save | Copies the results to Google Drive, folder `G31-04_outputs` |
| Optional push | Commits the updated docs, workbook and charts to GitHub |

### 1.5 Files for the course submission
| File | Where to find it after the run | Submit as |
|---|---|---|
| Cleaned dataset (CSV) | Drive: `G31-04_outputs/G31-04_Progress1_CleanedData.csv` | `G31-04_Progress1_CleanedData.csv` |
| Notebook (.ipynb) | Colab: **File > Download > Download .ipynb** | `G31-04_Progress1_DataPrep.ipynb` |
| Notebook PDF with outputs | Colab: **File > Print > Save as PDF** (after the run, so the outputs are inside) | `G31-04_Progress1_DataPrep.pdf` |
| Charts for slides and report | Drive: `G31-04_outputs/charts/*.png` | insert into the slides and report |

## 2. How to read the results

- **Cleaning log** (`docs/cleaning_log.md`, sheet `Cleaning_log`): every cleaning step with rows and columns before and after.
  Use it for the "cleaning steps" slide and Chapter 3.
- **Reconcile** (sheet `Reconcile`): our results next to the numbers written in the proposal. `OK` means the same within the
  rounding used in the proposal (column `tolerance`). Any `DIFF` must be explained or fixed in the report.
- **Comparison with the Progress 1 slides** (`outputs/compare_progress1.csv`): our counts next to the numbers on the
  Progress 1 slides. `DIFF` means the slides used another pipeline or definition. The group must agree on one source.
- **Data dictionary** (`docs/data_dictionary.md`, sheet `Data_dictionary`): every column, its type, meaning, an example value and why we use it.

### Charts (made by step 7, in `outputs/charts/`)
| File | What it shows | Use it for |
|---|---|---|
| `01_cleaning_funnel.png` | Rows after each main cleaning step, from the raw item data to the modelling table | Cleaning steps slide. Explains why the rows go down and then up |
| `02_kpi_trend.png` | KPI 1 (out-of-stock rate) and KPI 3 (demand on unavailable items) per week | KPI recap, dashboard |
| `03_top_categories.png` | Categories with the highest observed stock-out rate, latest week (KPI 2) | KPI recap, Q1 |
| `04_target_balance.png` | Stock-out share per prediction week, with the train / validate / test split | EDA: target balance |
| `05_views_distribution.png` | How rows spread over views in the last 7 days, and the stock-out rate in each group | EDA: distributions |
| `06_feature_correlation.png` | Spearman correlation of each feature with the target (train weeks only) | EDA: correlations, Q2 |
| `07_missing_values.png` | Share of empty values per column of the modelling table | Data quality issues slide |
| `08_raw_item_properties.png` | Raw item_properties file: the header and its first 5 rows, plus rows of the 2 properties we keep | Dataset or data dictionary slide: "what the raw data looks like" |
| `09_raw_events.png` | Raw events file: the header, its first 5 rows and the first purchase row | Dataset or data dictionary slide |
| `10_raw_category_tree.png` | Raw category tree: the header and its first rows | Dataset or data dictionary slide |
| `11_modelling_table.png` | Final modelling table: the header and its first 5 rows (9 of the columns) | Feature engineering slide |

Charts 08 to 11 show the real first rows of each file, read by the script. They are not made-up examples.

The chart titles state only what the data shows. Write the interpretation in the slide text or the report yourself.

## 3. The pipeline
| Step | Script | Does |
|---|---|---|
| 1 | `01_extract_raw.py` | Reads the raw files. Keeps the properties `available` and `categoryid`. Removes exact duplicate events. Starts a new cleaning log |
| 2 | `02_explore_snapshots.py` | Checks the 18 weekly snapshot dates (prints only) |
| 3 | `03_build_kpis.py` | Weekly item table, label (out of stock next week), "Unknown" and parent category, KPI tables, Reconcile |
| 4 | `04_demand_features.py` | Demand features |
| 5 | `05_docs.py` | Data dictionary and cleaning log (markdown and Excel sheets) |
| 6 | `06_export_compare.py` | Cleaned CSV for the submission, comparison with the Progress 1 slides |
| 7 | `07_charts.py` | All charts |

Definitions (snapshot, active, demand, label, category) are in `LOG.md` section 3. Every change is logged in `LOG.md`.

## 4. Optional: send the results back to GitHub from Colab
1. On GitHub: **Settings > Developer settings > Personal access tokens > Fine-grained tokens > Generate new token**.
   Repository access: only `g31-04-stockout-kpi`. Permission: **Contents: Read and write**.
2. In Colab: click the **key icon** (Secrets) on the left, add a secret named `GITHUB_TOKEN` with the token, and switch on
   notebook access. Never paste the token into a cell.
3. In the last cell, set `PUSH_TO_GITHUB` to True and fill `GIT_NAME` and `GIT_EMAIL`, then run that cell.

Without a token you can still download the files from the Drive folder and commit them on your laptop.

## 5. Run it on your own computer instead
Needs Python 3.12 or newer and about 4 GB RAM.
1. Put the 4 CSVs in `data_raw/` (or keep them in the folder above the repository).
2. Windows PowerShell: `powershell -ExecutionPolicy Bypass -File run_all.ps1`
3. Linux, macOS or Git Bash: `bash run_all.sh`

## 6. If something goes wrong
| Message | What to do |
|---|---|
| `FileNotFoundError: Not found in ...: [...]` | `RAW_DRIVE_DIR` is wrong, or the Drive folder is not in My Drive. Check the path in the Colab file browser (folder icon on the left) |
| `git clone` asks for a username or password | The repository is private. Add the `GITHUB_TOKEN` secret (section 4) |
| `RuntimeError: 0X_... failed` | Read the error printed above it. Run all again once; if it fails again, send the error to Rafi |
| Colab disconnected | Colab stops after some idle time. Run all again (about 5 to 10 minutes) |
| Numbers differ from the slides | Expected where `compare_progress1.csv` says `DIFF`. Do not edit numbers by hand; discuss which definition the group uses |
