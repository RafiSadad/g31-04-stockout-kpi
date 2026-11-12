"""Step 6: export the cleaned modelling table as CSV for the course submission, and compare our counts with
the numbers on the group's Progress 1 slides (12 Nov 2026).

Outputs: outputs/G31-04_Progress1_CleanedData.csv (not in git, too big), outputs/compare_progress1.csv
The slide numbers below are copied from the slide PDF, not computed. Our numbers are read from the cleaning log and the
KPI workbook, so they always come from the last run.
"""
import pandas as pd
from config import WORK_DIR, OUT_DIR
from cleanlog import PATH as LOG_PATH

mt = pd.read_csv(WORK_DIR / "modelling_table_features.csv.gz")
out = OUT_DIR / "G31-04_Progress1_CleanedData.csv"
mt.to_csv(out, index=False)
print(f"wrote {out} ({len(mt):,} rows x {mt.shape[1]} columns, {out.stat().st_size / 1e6:.1f} MB)")

log = pd.read_csv(LOG_PATH)
def after(action_start):
    r = log[log["action"].str.startswith(action_start)]
    return int(r.iloc[-1]["rows_after"]) if len(r) else None

x = pd.read_excel(OUT_DIR / "G31-04 KPI Tables.xlsx", sheet_name=None)
k2 = x["KPI2_by_week"].iloc[-1]
k3 = x["KPI3_demand_unavail"].set_index("snapshot")
k4 = x["KPI4_rule_by_split"].set_index("split")
ours = {
    "Item property rows (raw)": after("stack part 1 and part 2"),
    "Rows with available or categoryid": after("keep property in"),
    "Status rows, first record and changes only": after("count first record"),
    "Item-weeks with a known status": after("item-weeks with a known status"),
    "Events after cleaning": after("drop exact duplicate events"),
    "Modelling table rows": len(mt),
    "Stock-outs in modelling table": int(mt["y_next_out"].sum()),
    "Eligible categories, week 6 to 13 Sep": int(k2["eligible_categories"]),
    "High-risk categories, week 6 to 13 Sep": int(k2["high_risk_categories"]),
    "KPI3 demand on unavailable, 13 Sep (%)": float(k3.loc["2015-09-13", "demand_on_unavailable_pct"]),
    "Rule recall, test weeks (%)": round(100 * float(k4.loc["test", "recall"]), 1),
    "Rule precision, test weeks (%)": round(100 * float(k4.loc["test", "precision"]), 1),
}
slide = {   # Progress 1 slides, G31-04_Progress_1_slide_presentation_.pdf
    "Item property rows (raw)": 20275902, "Rows with available or categoryid": 2291853,
    "Status rows, first record and changes only": 588801, "Item-weeks with a known status": 6707888,
    "Events after cleaning": 2755641, "Modelling table rows": 282708, "Stock-outs in modelling table": 29214,
    "Eligible categories, week 6 to 13 Sep": 225, "High-risk categories, week 6 to 13 Sep": 22,
    "KPI3 demand on unavailable, 13 Sep (%)": 43.6, "Rule recall, test weeks (%)": 47.6, "Rule precision, test weeks (%)": 22.0,
}
cmp = pd.DataFrame({"check": list(ours), "ours": list(ours.values()), "progress1_slide": [slide[k] for k in ours]})
cmp["match"] = ["same" if o == s else "DIFF" for o, s in zip(cmp["ours"], cmp["progress1_slide"])]
cmp.to_csv(OUT_DIR / "compare_progress1.csv", index=False)
print(cmp.to_string(index=False))
