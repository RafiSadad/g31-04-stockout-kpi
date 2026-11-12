# Review: proposal and Progress 1 slides compared with the data

Group G31-04, Dataset S1. Written 12 Nov 2026 by Rafi (Data Engineer).

## Why this review
At Progress 1 the lecturer asked why the numbers were not consistent (for example "20 million rows, then 6 million") and
whether the data had been checked. This document goes through the proposal and the Progress 1 slides one by one and
compares every number with what the data gives.

## What the numbers here are based on
- **The data preparation notebook** `notebooks/G31-04_Progress1_DataPrep.ipynb`, run on the real data in Colab on 12 Nov 2026
  (its cleaning log and data quality checks). This is the notebook we submit, so **the slides must use its numbers**.
- For numbers the notebook does not print in those two files (KPI values, the rule baseline, the EDA percentages), the scripts in
  `scripts/` run on the real data on 12 Nov 2026, with the same definitions (snapshot, status carried forward, active = any event
  in the last 7 days, target = out of stock 7 days later, rows = in stock and active).
- Times are read as UTC. Nothing was changed to make a number match.

Verdicts: **OK** = same as the data. **WRONG** = different from the data; change it. **NOT CHECKED** = our notebook does not
compute it; the author must show where it comes from or remove it. **UNSUPPORTED** = a claim the data cannot show.
**EXPLAIN** = the number is right but needs one sentence of explanation.

## Summary
| Where | Main problems |
|---|---|
| Proposal | KPI 3 range (29-49%) and the number of categories (1,180) are wrong |
| Progress 1 slides | KPI 4 was taken out on purpose (group decision; the report must say so). Final table size (282,708 x 25), stock-out share (10.3%), high-risk base (225), rule baseline (47.6% / 22.0%) come from another pipeline; the feature list does not match the submitted notebook; slide 11 title must be removed; slide 5 needs an explanation for the row counts |

The other pipeline (`clean_data.py`, `build_features.py`) is not in the submission. Because the lecturer checks numbers against
the submitted code (guideline rule 7.4), every number on the slides must come from the submitted notebook.

---

## Part A. Proposal (report and proposal slides)

| Item | Proposal says | Data gives | Verdict | Change to |
|---|---|---|---|---|
| Total size | about 23 million rows, 4 files | 20,275,902 + 2,756,101 + 1,669 = 23,033,672 | OK | |
| Items | 417,053 | 417,053 | OK | |
| Visitors | 1,407,580 | 1,407,580 | OK | |
| **Categories** (report 2.1, slide 4) | **1,180** | **1,242** distinct `categoryid` values in item_properties (1,669 in the category tree) | **WRONG** | "1,242 categories used by items (1,669 in the category tree)" |
| item_properties rows | 20,275,902 | 20,275,902 | OK | |
| events rows, by type | 2,756,101 (view 2,664,312, addtocart 69,332, transaction 22,457) | same | OK | |
| category_tree | 1,669 rows, 25 top-level | 1,669, 25 | OK | |
| Snapshots | 18 weekly dates, 21 Jun missing | 18, 21 Jun missing | OK | |
| Items never in stock | 78% | 324,859 of 417,053 = 77.9% | OK | |
| Items with any events | 44% (56% without) | 185,246 of 417,053 = 44.4% | OK | |
| Weekly stock-out share | about 10%, between 4% and 24% | 4.4% (7 Jun) to 23.7% (17 May) | OK | |
| Status stays the same week to week | 85% to 96%, median 94% | | NOT CHECKED | show the code or remove |
| Modelling rows | 283,849, of which 29,502 (10.4%) stock-outs | 283,849 rows (notebook); 29,502 = 10.4% (scripts) | OK | |
| Category IDs not in tree | 30 | 30 | OK | |
| KPI 1, out-of-stock rate | 58% on 13 Sep, 59% on 6 Sep, range 43-60% | 58.0%, 59.4%, 42.6% to 60.1% | OK | |
| KPI 2, high-risk categories | 22 of 220 | 22 of 220 | OK | |
| KPI 3 on 13 Sep | 43% | 43.5% | OK (rounded down) | better "44%" or "43.5%" |
| **KPI 3 range** (report 1.2, slide 3) | **29% to 49%** | **21.9% (10 May) to 48.6% (2 Aug)** | **WRONG** | "22% to 49%" |
| Rule baseline, test weeks (proposal KPI 4, taken out later) | recall 0.42, precision 0.24, F1 0.30, 11.3% stock-outs | 0.42, 0.24, 0.30, 11.3% | OK | |

---

## Part B. Progress 1 slides (`G31-04_Progress_1_slide_presentation_.pdf`, 11 slides)

### Slide 1. Title
Names, roles and IDs are complete. **OK.**

### Slide 2. Recap: problem, user and KPIs
| Slide says | Data gives | Verdict |
|---|---|---|
| 3 KPIs, new order: KPI 1 high-risk categories, KPI 2 out-of-stock rate, KPI 3 demand on unavailable | The group took KPI 4 (model performance) out after the proposal, and changed the order | OK (group decision). Chapter 1 of the cumulative report must use the same list and order, and say in one sentence why KPI 4 was removed |
| 22 of **225** | 22 of **220** | **WRONG** (225 comes from the other pipeline) |
| 58% out-of-stock rate on 13 Sep | 58.0% | OK |
| **43.6%** demand on unavailable items | **43.5%** | **WRONG** (small, but the lecturer compares with the code) |
| "KPI values recomputed from the cleaned data" | | EXPLAIN: say which code and which definitions |

### Slide 3. Data dictionary: key columns
| Slide says | Data gives | Verdict |
|---|---|---|
| item_week_status: 6,707,888 rows | 6,707,888 item-weeks with a known status | OK (rows); the 10 columns are from the other pipeline |
| events_clean: 2,755,641 rows | 2,755,641 | OK (rows) |
| **model_table: 282,708 rows · 25 columns** | **283,849 rows · 28 columns** | **WRONG** |
| event_time "site time, UTC+3" | The files only have Unix milliseconds; the site time zone is not given anywhere | **UNSUPPORTED**: say "UTC" (what the notebook uses), or call UTC+3 an assumption |
| Column names (views_1w, addtocart_4w, n_changes_4w, oos_share_4w, top_category ...) | The notebook columns are views_1w, atc_4w, changes_4w, oos_share_4w, cat, parent_cat ... | **WRONG names**: use the notebook's data dictionary (section 6.1) |

### Slide 4. Data quality issues
| Slide says | Data gives | Verdict |
|---|---|---|
| 460 duplicate events, the only rows deleted | 460 removed | OK |
| 49,815 items with events but no stock data | 49,815 (255,585 events) | OK |
| 30 visitors with 1,000+ events, 3,386 purchases | 30, 61,184 events, 3,386 purchases | OK |
| 1,102 unreadable item properties | 1,102 | OK |
| 21 Jun missing, 14 Jun skipped | same | OK |
| 30 category IDs not in the tree | 30 | OK |
| "available = 0 means out of stock (items come back to 1, add-to-carts drop 10x)" | | NOT CHECKED in the notebook: show the code and numbers, or say it is still an assumption |

### Slide 5. Cleaning steps: before and after counts
This is the slide the lecturer asked about. **The numbers are right, but without an explanation they look inconsistent.**
| Slide says | Data gives | Verdict |
|---|---|---|
| 20,275,902 · 4 cols | 10,999,999 rows in part 1 + 9,275,903 rows in part 2 = 20,275,902; the 4 columns are timestamp, itemid, property, value. Notebook cell 1.1 (cleaning log steps 1.1) and a second count in cell 1.1b (line breaks in the files: lines - 1 header line) | OK |
| 2,291,853 · keep 2 of 1,104 properties | 2,291,853 (1,503,639 available + 788,214 categoryid) | OK |
| 588,801 · stock only, repeats dropped | 417,053 first records + 171,748 changes = 588,801 | OK, **EXPLAIN** |
| 6,707,888 · weekly grid | 417,053 items x 18 weeks = 7,506,954, minus 799,066 before the first record | OK, **EXPLAIN** |
| Events 2,756,101 → 2,755,641 | same | OK |
| Category tree 1,669 | 1,669 | OK |
| "All 18 steps are in cleaning_log.csv" | The submitted notebook logs 22 steps | **WRONG**: say 22, or show the notebook's cleaning log |

**Sentence to add on the slide:** "The raw item file is in long format: 1 row = 1 property value of 1 item at 1 time, for 1,104
properties. We keep 2 properties (2.29M rows). The stock status is repeated every week, so only 588,801 rows are a first record or a
change. We then build one row per item and week (417,053 items x 18 weeks, minus the weeks before an item's first record):
6.7M rows. The count goes up because the format changes, not because data is added."
The notebook's chart `07_rows_per_step.png` and `06_pipeline_tree.png` show this chain with the real numbers.

### Slide 6. Feature engineering
| Slide says | Data gives | Verdict |
|---|---|---|
| One row = an in-stock, active item at week t; target = out of stock at t + 7 days | same definition | OK |
| **282,708 rows · 25 columns · 10.3% stock-outs** | **283,849 rows · 28 columns · 10.4%** | **WRONG** |
| Train 10 · Valid 3 · Test 3 weeks | same | OK |
| Every feature uses only data before week t | The notebook checks this (cell 5.3: 300 random rows recounted from the data, 0 differences on the real data) | OK, and **add** the check to the slide |
| Feature list: item age, ever out of stock, weeks since last change, top-level group, level, share of the category out of stock, category size | Not in the submitted notebook. The notebook has: demand 1w/4w, demand trend, add-to-cart rate, buy rate, visitors, days since last purchase (+ flag), status changes, snapshots in the current status, share of the last 4 snapshots out of stock, category, parent category, category demand, item share of category demand | **WRONG**: list the notebook's features (its section 5 table gives the reason for each) |
| "Why: items in a category share suppliers" | There is no supplier data (out of scope in the proposal) | **UNSUPPORTED**: say "stock-out rates differ by category" |

### Slide 7. EDA 1: distributions
Values from the scripts on the real data (same definitions as the notebook; check them against the notebook chart `09_views_distribution.png`).
| Slide says | Data gives | Verdict |
|---|---|---|
| "all 282,708 rows" | 283,849 rows | **WRONG** |
| Share of rows by views: 0.7, 40.6, 19.0, 22.5, 10.6, 4.7, 1.7, 0.2 | 0.7, 40.5, 18.9, 22.5, 10.6, 4.7, 1.7, 0.2 | WRONG by 0.1 in two bins (other pipeline) |
| Stock-out rate by views: 7.6, 9.6, 10.1, 10.6, 11.4, 12.5, 13.7, 16.2 | 7.8, 9.7, 10.1, 10.7, 11.6, 12.4, 14.0, 16.6 | **WRONG** in most bins (other pipeline) |
| Median 2, max **762** views | median 2, max **782** | **WRONG** (max) |
| 88% of rows no add-to-cart, 96% no purchase; 32.8% were out of stock before, 16.3% vs 7.4% | | NOT CHECKED: take them from the notebook's summary, or remove |

### Slide 8. EDA 2: correlations
Values from the scripts on the real data (train weeks, Spearman). Compare with the notebook chart `10_feature_correlation.png`.
| Slide says | Data gives | Verdict |
|---|---|---|
| n_changes_4w 0.127 | changes_4w 0.128 | WRONG by 0.001 (other pipeline) |
| demand_trend 0.042 | 0.053 | **WRONG** |
| views_1w 0.023, addtocart_1w 0.014, views_4w -0.007 | 0.024, 0.014, -0.006 | small differences (other pipeline) |
| oos_share_4w 0.135, ever_out_of_stock 0.126, weeks_since_last_change -0.105, cat_oos_rate 0.070 | ever_out_of_stock, weeks_since_last_change and cat_oos_rate are not in the notebook; oos_share_4w is, with its own value | **WRONG**: use the notebook chart |
| Stock-out rate 4.8% to 20.5% across top-level categories | | NOT CHECKED |
| Interpretation (history matters more than views, signals are weak) | | fine as an interpretation, but write it from the notebook chart |

### Slide 9. EDA 3: target balance
| Slide says | Data gives | Verdict |
|---|---|---|
| **10.3%**, **29,214 of 282,708** rows | **10.4%**, **29,502 of 283,849** | **WRONG** |
| 17 May 23.7% | 23.7% | OK |
| 7 Jun **4.3%** | **4.4%** | **WRONG** (small) |
| 16 prediction weeks, no prediction for 14 Jun | same | OK |
| Judge by Recall, Precision, **F-beta**, PR-AUC | The proposal says Recall, Precision, **F1**, PR-AUC | **WRONG** vs proposal: use F1, or explain why F-beta |

### Slide 10. Data flow and next steps
| Slide says | Data gives | Verdict |
|---|---|---|
| clean_data.py, build_features.py | The submission is the notebook `G31-04_Progress1_DataPrep.ipynb` | **WRONG**: name the notebook sections; use its pipeline tree picture `06_pipeline_tree.png` |
| Model table 282,708 rows x 25 columns | 283,849 x 28 | **WRONG** |
| **Rule baseline recomputed: Recall 47.6%, Precision 22.0% (proposal reported 42% and 24%)** | Recall 42%, precision 24% on the cleaned test weeks | **WRONG**: the cleaned data still gives the proposal's values. (KPI 4 was taken out, but this baseline is still what the models must beat.) |
| "Feed risk scores into KPI 1" | With the new KPI list, KPI 1 = high-risk categories, which uses the risk score | OK |

### Slide 11. "Fixing data numbers to be relate with the slide"
**Remove this slide.** The title says that data numbers were changed to fit the slide. That is the opposite of what we do (the
slides must follow the data), and it is exactly what the lecturer was worried about (guideline rule 7.4).

---

## What to do
1. Data Analyst: update proposal 1.2 and 2.1 in the cumulative report: the new KPI list (3 KPIs, new order, why KPI 4 was
   removed), the KPI 3 range (22-49%) and 1,242 categories.
2. Slides 2, 3, 5, 6, 7, 8, 9, 10: take every number and chart from the submitted notebook run (`G31-04-OUTPUT`), not from
   the other pipeline. Delete slide 11.
3. Slide 5: add the long-format explanation above and the rows-per-step chart.
4. Items marked NOT CHECKED: whoever made them shows the code, or the item is removed.
5. Keep one source of numbers from now on: the submitted notebook. If a definition changes, change the notebook, run it again
   and update the slides from the new output.
