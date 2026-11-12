# NOTES: status and context for the next session

Last update: 4 Nov 2026 (evening). Read this after `README.md` and `LOG.md`.
Rafi works on Windows PowerShell. Raw CSVs are in the folder above the repo (`..`). Run everything with
`powershell -ExecutionPolicy Bypass -File run_all.ps1`. Always `git pull` first.

## 1. Course deadlines that matter for Rafi (INC362 guideline)
| Milestone | Presentation | LEB2 deadline | Q&A to |
|---|---|---|---|
| Proposal | Thu 5 Nov 2026, 13:30 | Wed 4 Nov, 23:55 | all members (Rafi presents the plan slides) |
| **Progress 1** | **Thu 12 Nov 2026, 13:30** | **Wed 11 Nov, 23:55** | **Data Engineer (Rafi)** |
| Progress 2 | Thu 19 Nov | Wed 18 Nov | Data Analyst, Data Scientists |
| Final | Wed 9 Dec | Tue 8 Dec, 18:00 | all members |

Rules to remember: all members must attend or the team gets 0; 10% off per day late; any number that does not match
the submitted code gives the whole team 0 (rule 7.4); file names start with the Group ID, e.g. `G31-04_Progress1_Report.pdf`.

## 2. Status of Rafi's tasks (Member 5, Data Engineer)
Done and on `main`:
- KPI data tables (`outputs/G31-04 KPI Tables.xlsx`), Reconcile 15 of 16 OK (known DIFF: KPI3 min).
- Data flow diagram (`docs/data_flow.png`), draft for Peeranat to check.
- Data dictionary (`docs/data_dictionary.md`), cleaning log 21 steps (`docs/cleaning_log.md`).
- 9 demand features (`scripts/04_demand_features.py`), "Unknown" category and parent category (`scripts/03_build_kpis.py`).
- README with scope and messages for the group, `run_all.ps1` (tested on Windows).

**To do for Progress 1 (submission checklist, guideline section 8):**
1. Cleaned dataset CSV: planned `G31-04_Progress1_CleanedData.csv` from the modelling table (new step 6). Too big for GitHub, upload to LEB2.
2. Notebook `.ipynb` plus PDF with outputs: planned `G31-04_Progress1_DataPrep.ipynb` that runs steps 1 to 6 and shows the cleaning log,
   feature summary and data flow diagram. Rafi runs it on his laptop and exports the PDF.
3. Prepare for Q&A: be able to explain every cleaning step and every feature (use `docs/cleaning_log.md`, `docs/data_dictionary.md`, `LOG.md` sections 3, 8, 9).

## 2b. Since 12 Nov: processing runs in Google Colab
- Notebook: `notebooks/G31-04_DataPrep_Colab.ipynb`. It clones this repo, copies the raw CSVs from Google Drive to `data_raw/`, runs steps 1 to 6.
- Progress 1 problem (12 Nov): the lecturer asked why the numbers changed (20M rows, then 6.7M) and suspected unchecked AI output.
  Explanation and fixes are in `LOG.md` section 12. The group has two pipelines with slightly different numbers; the slides use the other one
  (`clean_data.py`, `build_features.py`, owner to confirm). The group must choose ONE source of numbers.
- Step 7 (`07_charts.py`) makes all charts in `outputs/charts/`. English guide for the group: `HOW_TO_USE.md`.
- Next: Rafi runs the notebook on the real data, then checks `outputs/compare_progress1.csv`, Reconcile and the charts.

## 3. Open decisions (waiting for the group)
- Category backfill: fill an item's category from later weeks? Removes most of the 29,358 "Unknown" rows (90% in the first 5 weeks) but uses a later record. Peeranat and the Data Scientists decide.
- Proposal numbers: KPI 3 range 29 to 49% (data 21.9 to 48.6%); 1,180 categories (data 1,242). Hill (Data Analyst) decides.
- Meaning of `available = 0`: Peeranat's task.
- Which Data Scientist does which task: report 2.6 and slides disagree. Not Rafi's decision.

## 3b. Decisions taken
- 5 Nov 2026: target user stays **Head of Inventory**. Sales and a conversion (CRO) manager were considered and rejected: no prices or revenue,
  no page, traffic or session data, and changing the user would mean a new target, a new table and new KPIs after the proposal.
  Answer if asked: we have no stock quantities, only a weekly available flag, so we predict "becomes unavailable next week", not "how many units
  to order" (out of scope). KPI 3 (about 43% of interest goes to unavailable items) also helps a sales or conversion team.
- Idea for Progress 1 EDA (not started): does the add-to-cart per view ratio drop when `available = 0`? Also helps to check what `available = 0` means.

## 4. Team and Discord
Members (proposal): Sirawich Moonmangmee (Leader, Data Analyst), Peeranat Charungrattanapong (Data Engineer),
Pakkapon Rattanaumpawan (Data Scientist), Arnakorn Khemtaronon (Data Scientist), Rafi Sadad Ar Rabban (Data Engineer, Member 5).
The team is Thai, so everything in the repo and on Discord is in English.
Discord handles: `@supervisor` = Hill (leads the slides and the report). Other handles (`ᚾᛁᚾᛖ`, `ViperX`, `o2dong`) are not mapped to names yet.

| Channel | Used for |
|---|---|
| #general | chat, meeting times, Google Drive data link, who presents which slide |
| #problem | problem statement drafts |
| #kpi | KPI definitions (the draft there uses 1,242 categories) |
| #scope | scope draft (report 1.4) |
| #dataset | dataset facts, timestamp to date conversion, PR-AUC explanation |
| #plan | project plan (content not seen yet) |
| #report | report review (Hill asked Rafi to check the report here) |
| #file-project | shared files (content not seen yet) |
| #slide | Canva slides (content not seen yet) |

Data: Google Drive folder https://drive.google.com/drive/folders/1-_Qns7aF7vowcg9gIa5i7x6i3qTCtGDm
Slides: Canva link is in #general.

## 5. Discord messages drafted on 4 Nov (send order: #slide, #report, #file-project, #dataset)
Status (4 Nov, evening): #report, #file-project and #dataset were **sent**. #slide was **not sent**: the slides were already fixed in Canva. Wait for replies from Hill (2 proposal numbers) and Peeranat (category backfill).

**#slide**
```
@supervisor Hill, quick check on Canva before tomorrow:
1. Slide 1 needs members AND roles (guideline). My name is missing: Rafi Sadad Ar Rabban, Data Engineer.
2. The plan slide needs "who does what by when". Can I add my row? Rafi (DE): KPI data tables + data flow diagram (3 to 4 Nov); data dictionary, demand features, Unknown category, cleaning log (7 to 9 Nov, already done).
3. Guideline says 7 to 9 slides. The PDF I have shows 10. Is the Canva one already 9?
4. Small typo in the slide 1 script: "Group 631-04" should be "G31-04".
```

**#report**
```
@supervisor Hill, I checked the numbers in the report with the script. Almost everything matches. Only 2 things:
1. KPI 3 range: report says 29 to 49%, data gives 21.9 to 48.6%. The low weeks are 10 and 17 May. Maybe write "22 to 49%"?
2. Report 2.1 says 1,180 categories, but the data has 1,242 (same as our #kpi draft). Which one do we use?
For Chapter 3 you can copy the cleaning log and data dictionary from the GitHub link in #file-project.
```

**#file-project**
```
Hi guys, my DE part for next week is done and uploaded.
https://github.com/RafiSadad/g31-04-stockout-kpi
What's inside: data dictionary, cleaning log (rows and columns before/after each step), 9 demand features with reasons,
missing category fixed ("Unknown") + parent category, KPI tables, data flow diagram.
All numbers are from the real data and still match the proposal (283,849 rows, 10.4% stock-outs, 22/220 categories, recall 0.42).
What each of you can use: https://github.com/RafiSadad/g31-04-stockout-kpi#6-messages-for-the-group
The CSVs are not on GitHub (too big), use our Drive folder.
```

**#dataset**
```
For the DE and DS:
- The modelling table now has 26 columns. Target = y_next_out. Column guide is in the README.
- Question for our other DE: many items get their category only some weeks later (90% of "Unknown" rows are in the first 5 weeks). Can we fill the category from later weeks, or is that leakage? Let's decide together.
- Parent category is ready, so we can roll up to parent level like in our scope draft.
- available = 0 meaning is still not confirmed.
```

## 6. Files Rafi shared in the session (not in the repo)
Proposal report PDF, S1 summary PDF, slides PDF (10 pages, Rafi missing on title and plan slides), an older report
version from 2 Nov (Rafi's name missing in the member list), the course guideline PDF, `category_tree.csv`, the KPI xlsx (identical to `main`).
Ask Rafi to upload them again if needed.
