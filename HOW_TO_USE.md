# How to use this repository

Group G31-04, Dataset S1. This guide is for every group member. You do not need to install anything if you use Google Colab.

**The one rule:** every number and chart in our slides and report must come from these scripts. Never type or change a
number by hand. If something must change, change the script, run everything again, and use the new outputs.

## 0. The data preparation notebook (for the submission and for the lecturer)
**File:** `notebooks/G31-04_Progress1_DataPrep.ipynb`. This is the file to submit. All code is inside; it needs only the
4 raw CSV files. It shows the whole data preparation as one readable process:

| Section | What happens |
|---|---|
| 0 | Setup and the 4 raw files |
| 1 | Load the raw data and look at it (columns, first rows, types, time range) |
| 2 | Data quality checks: each issue, how many rows, and what we decide |
| 3 | Cleaning (row and column counts before and after each step) |
| 4 | Weekly item table and the target (out of stock next week) |
| 5 | Feature engineering with the reason for each feature, and a leakage check that recounts 300 random rows from the data |
| 6 | Final model-ready dataset and its data dictionary |
| 7 | Pictures of each raw file (both item_properties parts too), the data pipeline tree, and initial EDA charts |
| 8 | Save everything |

**How to run**
1. Open it in Colab (*File > Upload notebook*, or open it from Google Drive).
2. Cell 0.2 decides where the raw files come from:
   - `USE_MY_DRIVE` (on): if your Drive has `My Drive/Colab Notebooks/G31-04/G31-04-RAW` with the 4 CSVs and `.../G31-04-OUTPUT`,
     the raw files are read from there and all results are saved there. Colab asks once to connect Google Drive.
   - Without that folder (for example the lecturer), nothing is read from or written to Drive and `RAW_SOURCE` is used:
     `download` (default, public link, no sign-in), `upload` (pick the files or one zip) or `folder` (a path).
3. **Runtime > Run all**. About 5 to 10 minutes.
4. Results: folder `G31-04_run/outputs` and `G31-04_Progress1_results.zip` (downloaded at the end; with `USE_MY_DRIVE` also in `G31-04-OUTPUT`):
   `G31-04_Progress1_CleanedData.csv` (the final dataset), `G31-04_Progress1_DataPrep.xlsx` (cleaning log, data quality checks,
   data dictionary, column summary, first rows), the same tables as CSV files, and 11 pictures and charts, including
   `06_pipeline_tree.png`: every table from the 4 raw files to the final table, with its rows x columns, and every step between them.
5. Submission: after the run, *File > Download > Download .ipynb* (with outputs) and *File > Print > Save as PDF*.

The notebook does not compare its results with the proposal or with earlier runs. The numbers are what the data gives with the
definitions written in section 4 of the notebook.

## 1. Run the repository version in Google Colab (for the group)

### 1.1 Where the data and the results are
The notebook works with **Google Drive folder links**. Cell 1 already has the group folders:
- `RAW_DRIVE_DIR`: folder with the 4 raw CSV files (`item_properties_part1.csv`, `item_properties_part2.csv`, `events.csv`, `category_tree.csv`)
- `SAVE_DRIVE_DIR`: folder `G31-04-OUTPUT` for the results

Both folders are shared as "Anyone with the link: Editor". The links are already saved in cell 1, so you do not type them again.
To use other folders, paste their links into cell 1. A path such as `/content/drive/MyDrive/G31-04` also works (then Drive is mounted instead).

**Do I have to sign in to Google?**
- *Reading the raw data: no.* The notebook downloads the 4 CSVs without a sign-in, because the folder is shared with the link.
  If Google blocks that download (for example a download quota), the notebook asks you to sign in and tries again.
- *Saving the results to the results folder: yes.* Google does not allow uploads without a sign-in, even to a folder shared with
  "anyone with the link". So the sign-in window appears only in the last cell. If you skip it, nothing is lost: the same cell also
  makes `G31-04_results.zip` and your browser downloads it.

### 1.2 Open the notebook
- If the repository is public, open this link:
  https://colab.research.google.com/github/RafiSadad/g31-04-stockout-kpi/blob/main/notebooks/G31-04_DataPrep_Colab.ipynb
- If the repository is private: download `notebooks/G31-04_DataPrep_Colab.ipynb` from GitHub, then in Colab choose
  **File > Upload notebook**. Also add a GitHub token as a Colab secret (see section 4).

### 1.3 Run it
1. Check cell 1 (Settings). The folder links are already filled in. The raw folder may hold the 4 CSV files or a zip with them.
2. Choose **Runtime > Run all**.
3. Cell 3 downloads the 4 CSVs (about 1 GB, 1 to 3 minutes). No sign-in is needed for this.
   At the very end, a Google sign-in window opens for saving to the results folder. Choose your Google account and allow access.
4. Wait about 5 to 10 minutes. Each step prints what it did. If a step fails, the notebook stops and shows the error (see section 5).

### 1.4 What the notebook does
| Cell | What happens |
|---|---|
| 1. Settings | Paths for the raw data and for the results |
| 2. Drive and GitHub | Clones (or updates) this repository and defines the Drive helpers (a path in cell 1 mounts Drive instead) |
| 3. Raw files | Downloads the 4 CSVs into `data_raw/` inside the repository without a sign-in (extracts them from a zip if needed). If the public download fails, it signs in and checks the file sizes against Drive |
| 4. Libraries | Installs `requirements.txt` and prints the versions used |
| Steps 1 to 7 | Runs the numbered scripts in `scripts/` (table in section 3) |
| Results | Shows the cleaning log, Reconcile, the comparison with the Progress 1 slides, the feature summary, the diagrams and all charts |
| Save | Makes `G31-04_results.zip` (your browser downloads it), then uploads the results to the results folder (`G31-04-OUTPUT`) after a Google sign-in. A file with the same name is replaced, so there are no duplicates. Charts go into a `charts` sub-folder |
| Optional push | Commits the updated docs, workbook and charts to GitHub |

### 1.5 Files for the course submission
| File | Where to find it after the run | Submit as |
|---|---|---|
| Cleaned dataset (CSV) | Drive: `G31-04-OUTPUT/G31-04_Progress1_CleanedData.csv` | `G31-04_Progress1_CleanedData.csv` |
| Notebook (.ipynb) | Colab: **File > Download > Download .ipynb** | `G31-04_Progress1_DataPrep.ipynb` |
| Notebook PDF with outputs | Colab: **File > Print > Save as PDF** (after the run, so the outputs are inside) | `G31-04_Progress1_DataPrep.pdf` |
| Charts for slides and report | Drive: `G31-04-OUTPUT/charts/*.png` | insert into the slides and report |

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
| `FileNotFoundError: Not found in ...: [...]` | The raw folder link in cell 1 is wrong, or the 4 files have other names. With a path: the folder is not in My Drive |
| `HttpError 404` or `403` after a sign-in | The Google account you chose cannot open that folder. Ask the owner to share it with that account (editor for the results folder), or use the zip |
| `Download without sign-in did not work` | Not an error. Google blocked the public download (often a quota on large files), so the notebook signs in and downloads through your account |
| `Could not save to Google Drive` | You skipped the sign-in or the account has no edit access. Use the zip your browser downloaded, or run the save cell again |
| `SIZE DIFFERS FROM DRIVE` in cell 3 | The download was cut off. Delete `data_raw/` in the Colab file browser and run cell 3 again |
| `git clone` asks for a username or password | The repository is private. Add the `GITHUB_TOKEN` secret (section 4) |
| `RuntimeError: 0X_... failed` | Read the error printed above it. Run all again once; if it fails again, send the error to Rafi |
| Colab disconnected | Colab stops after some idle time. Run all again (about 5 to 10 minutes) |
| Numbers differ from the slides | Expected where `compare_progress1.csv` says `DIFF`. Do not edit numbers by hand; discuss which definition the group uses |
