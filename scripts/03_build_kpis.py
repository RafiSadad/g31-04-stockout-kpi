"""Step 3: build the weekly item table and the 4 KPI tables.

Definitions (follow G31-04 Proposal, Chapter 1.2 and 2.2):
  state(item, t)  = last known value of `available` at or before snapshot t (forward fill). 1 = in stock, 0 = out.
  active(item, t) = at least one event (view, addtocart, transaction) in (t - 7 days, t].
  demand          = views + add-to-carts in (t - 7 days, t].
  next-week label = state at the snapshot exactly 7 days after t (needs that snapshot to exist).
  category        = last known categoryid at or before t. If there is none, cat = -1 ("Unknown") and cat_missing = 1.
  parent category = parentid of cat in category_tree.csv. A top-level category is its own parent. If cat is Unknown or
                    not in the tree, parent_cat = -1 ("Unknown") and cat_in_tree = 0.
                    "Unknown" is kept in the modelling table and shown in the KPI sheets, but it is not ranked in KPI 2.
Outputs: work/modelling_table.csv.gz, work/item_week.csv.gz (input for step 4) and outputs/G31-04 KPI Tables.xlsx
Row and column counts of each cleaning step go to work/cleaning_log.csv.
"""
import numpy as np
import pandas as pd
from config import DATA_DIR, WORK_DIR, OUT_DIR, UNKNOWN_CAT
from cleanlog import CleanLog

DAY = 86_400_000
log = CleanLog("03_build_kpis")
p = pd.read_csv(WORK_DIR / "item_props_small.csv.gz", dtype={"value": "string"})
log.add("load step 1 output", "item_props_small", (0, 0), p.shape)
ev = pd.read_csv(WORK_DIR / "events_clean.csv.gz", usecols=["timestamp", "event", "itemid"])
log.add("load cleaned events (3 of 5 columns)", "events_clean", (0, 0), ev.shape, "visitorid and transactionid not needed here")

# ---------- snapshots and state matrices (items x snapshots) ----------
a0 = p[p.property == "available"]
a = a0.drop_duplicates(["itemid", "timestamp"], keep="last")
log.add("drop duplicate (itemid, timestamp) for available", "available rows", a0.shape, a.shape, "keep the last row")
_s = a.sort_values(["itemid", "timestamp"])
n_first_or_change = int((_s["value"] != _s.groupby("itemid")["value"].shift()).sum())
log.add("count first record and each status change (check only)", "available rows", a.shape, (n_first_or_change, a.shape[1]),
        "the status is repeated every week even without a change; this count is not used further")
snaps = np.sort(a["timestamp"].unique())
dates = pd.to_datetime(snaps, unit="ms").strftime("%Y-%m-%d")
S = a.pivot(index="itemid", columns="timestamp", values="value").astype(float).reindex(columns=snaps)
na_before = int(S.isna().sum().sum())
log.add("pivot available to item x snapshot status matrix", "status matrix", a.shape, S.shape,
        f"rows = items, columns = {len(snaps)} snapshots; empty cells: {na_before:,}")
S = S.ffill(axis=1)                       # carry the last known status forward
na_after = int(S.isna().sum().sum())
log.add("forward fill status across snapshots", "status matrix", S.shape, S.shape,
        f"empty cells {na_before:,} -> {na_after:,} (left empty = before the first known status)")
items = S.index
n_known = int(S.notna().sum().sum())
log.add("item-weeks with a known status (long format: itemid, snapshot, status)", "status matrix -> item-week rows",
        (S.size, 3), (n_known, 3), f"{len(items):,} items x {len(snaps)} snapshots = {S.size:,}, minus {na_after:,} before the first status")
c0 = p[p.property == "categoryid"]
c = c0.drop_duplicates(["itemid", "timestamp"], keep="last")
log.add("drop duplicate (itemid, timestamp) for categoryid", "categoryid rows", c0.shape, c.shape, "keep the last row")
C = c.pivot(index="itemid", columns="timestamp", values="value").astype(float)
C = C.reindex(columns=sorted(set(C.columns) | set(snaps))).ffill(axis=1)[snaps].reindex(items)
log.add("category per item and snapshot (last known, forward fill)", "category matrix", c.shape, C.shape,
        f"rows = items with a status; {int(C.isna().any(axis=1).sum()):,} items have at least one snapshot without a category")
# Missing category: either the item never has a categoryid, or its first categoryid comes after the snapshot.
never = ~C.index.isin(c["itemid"].unique())
n_miss = int(C.isna().sum().sum())
n_never = int(C[never].isna().sum().sum())
C = C.fillna(UNKNOWN_CAT)
log.add('fill missing category with "Unknown" (cat = -1)', "category matrix", C.shape, C.shape,
        f"cells filled: {n_miss:,} ({n_never:,} where the item never has a categoryid, {n_miss - n_never:,} where it is only known later)")
Sv, Cv = S.to_numpy(), C.to_numpy()

# parent category from the category tree (small file, read whole)
tree = pd.read_csv(DATA_DIR / "category_tree.csv")
log.add("load category tree", "category_tree", (0, 0), tree.shape,
        f"{int(tree['parentid'].isna().sum())} top-level categories have no parent")
PARENT = {int(c): int(c if pd.isna(p) else p) for c, p in zip(tree["categoryid"], tree["parentid"])}
item_cats = set(c["value"].astype(float).astype(int))
not_in_tree = sorted(item_cats - set(PARENT))
print("items:", len(items), "snapshots:", len(snaps))

# ---------- demand per snapshot ----------
n0 = ev.shape
ev = ev[ev["event"].isin(["view", "addtocart", "transaction"])]
log.add("keep event in {view, addtocart, transaction}", "events", n0, ev.shape)
def window(t, days):
    w = ev[(ev["timestamp"] > t - days * DAY) & (ev["timestamp"] <= t)]
    return w.groupby(["itemid", "event"]).size().unstack(fill_value=0).reindex(columns=["view", "addtocart", "transaction"], fill_value=0)

frames = {}
for j, t in enumerate(snaps):
    w1, w4 = window(t, 7), window(t, 28)
    d = pd.DataFrame(index=items)
    d["state"] = Sv[:, j]
    d["cat"] = Cv[:, j].astype("int64")
    d["cat_missing"] = (d["cat"] == UNKNOWN_CAT).astype(int)
    d["parent_cat"] = d["cat"].map(PARENT).fillna(UNKNOWN_CAT).astype("int64")
    d["cat_in_tree"] = d["cat"].isin(list(PARENT)).astype(int)
    for col, nm in (("view", "views"), ("addtocart", "atc"), ("transaction", "tx")):
        d[f"{nm}_1w"] = w1[col].reindex(items).fillna(0).to_numpy()
        d[f"{nm}_4w"] = w4[col].reindex(items).fillna(0).to_numpy()
    d["demand_1w"] = d["views_1w"] + d["atc_1w"]
    d["active"] = (d["views_1w"] + d["atc_1w"] + d["tx_1w"]) > 0
    # number of status changes in the last 4 snapshot steps
    lo = max(0, j - 4)
    seg = Sv[:, lo:j + 1]
    d["changes_4w"] = (np.abs(np.diff(seg, axis=1)) > 0).sum(axis=1) if seg.shape[1] > 1 else 0
    frames[j] = d

# ---------- KPI 1 and KPI 3 (per snapshot) ----------
k1, k3 = [], []
for j in range(len(snaps)):
    d = frames[j]
    act = d[d["active"] & d["state"].notna()]
    oos = int((act["state"] == 0).sum())
    k1.append({"snapshot": dates[j], "active_items": len(act), "active_out_of_stock": oos,
               "oos_rate_pct": round(100 * oos / len(act), 1)})
    tot = d["demand_1w"].sum()
    un = d.loc[d["state"] == 0, "demand_1w"].sum()
    k3.append({"snapshot": dates[j], "views_plus_addtocart_7d": int(tot), "on_unavailable_items": int(un),
               "demand_on_unavailable_pct": round(100 * un / tot, 1)})
k1, k3 = pd.DataFrame(k1), pd.DataFrame(k3)

# ---------- modelling table, KPI 2 (per week) and KPI 4 ----------
rows, k2w, k4w = [], [], []
cat_last = None
for j in range(len(snaps) - 1):
    if snaps[j + 1] - snaps[j] != 7 * DAY:      # skip weeks whose next snapshot is missing (14 Jun -> 28 Jun)
        continue
    d = frames[j]
    el = d[(d["state"] == 1) & d["active"]].copy()
    el["y_next_out"] = (Sv[:, j + 1][items.get_indexer(el.index)] == 0).astype(int)
    el["snapshot"] = dates[j]
    rows.append(el)
    # KPI 2: observed stock-out rate per category (stand-in for the model risk score)
    g = el.groupby("cat").agg(eligible_items=("y_next_out", "size"), observed_stockouts=("y_next_out", "sum"),
                              demand=("demand_1w", "sum"))
    g["wd"] = (el["demand_1w"] * el["y_next_out"]).groupby(el["cat"]).sum()
    g["observed_stockout_rate_pct"] = (100 * g["observed_stockouts"] / g["eligible_items"]).round(1)
    g["demand_weighted_risk"] = np.where(g["demand"] > 0, (100 * g["wd"] / g["demand"]).round(1), np.nan)
    g = g.drop(columns="wd")
    unk = g[g.index == UNKNOWN_CAT]               # "Unknown" is shown but never ranked: it is not a real category
    g = g[g.index != UNKNOWN_CAT]
    ok = g[g["eligible_items"] >= 20].sort_values("observed_stockout_rate_pct", ascending=False)
    n_el = len(ok); n_high = int(round(0.10 * n_el))
    k2w.append({"snapshot": dates[j], "next_snapshot": dates[j + 1], "eligible_categories": n_el, "high_risk_categories": n_high,
                "unknown_category_items": int(unk["eligible_items"].sum())})
    if j == len(snaps) - 2:                       # latest usable week: 6 Sep -> 13 Sep
        g["tier"] = "low data (<20 items)"
        ok = ok.copy()
        ok["tier"] = ["High"] * n_high + ["Medium"] * int(round(0.20 * n_el)) + ["Low"] * (n_el - n_high - int(round(0.20 * n_el)))
        unk = unk.assign(tier="Unknown category (not ranked)")
        cat_last = pd.concat([ok, g[g["eligible_items"] < 20].sort_values("eligible_items", ascending=False), unk]).reset_index()
        cat_last = cat_last.rename(columns={"cat": "categoryid"})
    # KPI 4 rule: predict stock-out when the item changed status in the last 4 weeks
    pred = (el["changes_4w"] > 0).astype(int)
    tp = int(((pred == 1) & (el["y_next_out"] == 1)).sum()); fp = int(((pred == 1) & (el["y_next_out"] == 0)).sum())
    fn = int(((pred == 0) & (el["y_next_out"] == 1)).sum()); tn = int(((pred == 0) & (el["y_next_out"] == 0)).sum())
    k4w.append({"snapshot": dates[j], "rows": len(el), "stockouts": int(el["y_next_out"].sum()), "TP": tp, "FP": fp, "FN": fn, "TN": tn})

mt = pd.concat(rows)
pooled = (len(items) * len(snaps), frames[0].shape[1])
log.add("stack item x snapshot tables", "item x snapshot", (len(items), frames[0].shape[1]), pooled,
        f"{len(items):,} items x {len(snaps)} snapshots")
n_weeks = len(rows)
log.add("drop weeks whose next snapshot is not 7 days later", "item x snapshot", pooled, (len(items) * n_weeks, pooled[1]),
        f"{len(snaps) - n_weeks} snapshots dropped (no label), {n_weeks} prediction weeks left")
log.add("keep in-stock and active items, add label y_next_out and snapshot", "item x snapshot -> modelling table",
        (len(items) * n_weeks, pooled[1]), (mt.shape[0], mt.shape[1] + 1),
        f"+1 column = itemid index; rows with Unknown category: {int(mt['cat_missing'].sum()):,}")
known = mt["cat_missing"] == 0
log.add('map category to parent category (unknown parent -> "Unknown")', "modelling table", (mt.shape[0], mt.shape[1] + 1), (mt.shape[0], mt.shape[1] + 1),
        f"{len(not_in_tree)} of {len(item_cats)} categoryid values in item_properties are not in category_tree "
        f"({int((known & (mt['cat_in_tree'] == 0)).sum()):,} modelling rows); "
        f"{int((known & (mt['parent_cat'] == mt['cat'])).sum()):,} modelling rows have a top-level category (own parent)")
mt.to_csv(WORK_DIR / "modelling_table.csv.gz", index_label="itemid")
# small table of all active items per snapshot (any status), used by step 4 for category demand
iw = pd.concat([frames[j].loc[frames[j]["active"], ["cat", "demand_1w"]].assign(snapshot=dates[j]) for j in range(len(snaps))])
iw.to_csv(WORK_DIR / "item_week.csv.gz", index_label="itemid")
k2w, k4 = pd.DataFrame(k2w), pd.DataFrame(k4w)

def split_of(d):
    return "train" if d <= "2015-07-26" else "validate" if d <= "2015-08-16" else "test"
k4["split"] = k4["snapshot"].map(split_of)
def metrics(df):
    s = df[["rows", "stockouts", "TP", "FP", "FN", "TN"]].sum()
    r = s.TP / (s.TP + s.FN); pr = s.TP / (s.TP + s.FP); f1 = 2 * r * pr / (r + pr)
    return pd.Series({**s.astype(int).to_dict(), "stockout_share_pct": round(100 * s.stockouts / s.rows, 1),
                      "recall": round(r, 2), "precision": round(pr, 2), "f1": round(f1, 2)})
k4["recall"] = (k4.TP / (k4.TP + k4.FN)).round(2); k4["precision"] = (k4.TP / (k4.TP + k4.FP)).round(2)
k4["f1"] = (2 * k4.recall * k4.precision / (k4.recall + k4.precision)).round(2)
k4_split = k4.groupby("split").apply(metrics, include_groups=False).reindex(["train", "validate", "test"])
k4_split.loc["ALL"] = metrics(k4)

# ---------- KPI 3 by category (latest snapshot) and watch list ----------
dl = frames[len(snaps) - 1]
cat3 = dl.groupby("cat").agg(demand=("demand_1w", "sum")).join(
    dl[dl["state"] == 0].groupby("cat")["demand_1w"].sum().rename("demand_on_unavailable"))
cat3["demand_on_unavailable"] = cat3["demand_on_unavailable"].fillna(0)
cat3 = cat3[cat3["demand"] > 0]
cat3["demand_on_unavailable_pct"] = (100 * cat3["demand_on_unavailable"] / cat3["demand"]).round(1)
cat3 = cat3.sort_values("demand", ascending=False).reset_index().rename(columns={"cat": "categoryid"})
wl = dl[(dl["state"] == 1) & dl["active"] & (dl["changes_4w"] > 0)].sort_values("demand_1w", ascending=False).head(50)
wl = wl.reset_index()[["itemid", "cat", "views_1w", "atc_1w", "changes_4w"]].rename(
    columns={"cat": "categoryid", "views_1w": "views_7d", "atc_1w": "addtocart_7d", "changes_4w": "status_changes_4wk"})
wl["predicted_p_stockout"] = "to be added (model)"

# ---------- reconciliation with the proposal ----------
last = len(snaps) - 1
k1d = k1.set_index("snapshot"); k3d = k3.set_index("snapshot")
n_hi = int(k2w.iloc[-1]["high_risk_categories"]); n_el = int(k2w.iloc[-1]["eligible_categories"])
tot_rows, tot_pos = int(mt.shape[0]), int(mt["y_next_out"].sum())
t = k4_split.loc["test"]
rec = pd.DataFrame([
    ("KPI1 OOS rate on 13 Sep (%)", 58, k1d.loc["2015-09-13", "oos_rate_pct"], 0.5),
    ("KPI1 OOS rate on 6 Sep (%)", 59, k1d.loc["2015-09-06", "oos_rate_pct"], 0.5),
    ("KPI1 min over 18 dates (%)", 43, k1["oos_rate_pct"].min(), 0.5),
    ("KPI1 max over 18 dates (%)", 60, k1["oos_rate_pct"].max(), 0.5),
    ("KPI2 eligible categories", 220, n_el, 0),
    ("KPI2 high-risk categories", 22, n_hi, 0),
    ("KPI3 demand on unavailable 13 Sep (%)", 43, k3d.loc["2015-09-13", "demand_on_unavailable_pct"], 0.5),
    ("KPI3 min (%)", 29, k3["demand_on_unavailable_pct"].min(), 0.5),
    ("KPI3 max (%)", 49, k3["demand_on_unavailable_pct"].max(), 0.5),
    ("Modelling rows", 283849, tot_rows, 0),
    ("Stock-outs in modelling table", 29502, tot_pos, 0),
    ("Stock-out share overall (%)", 10.4, round(100 * tot_pos / tot_rows, 1), 0.05),
    ("KPI4 rule recall (test)", 0.42, t["recall"], 0.005),
    ("KPI4 rule precision (test)", 0.24, t["precision"], 0.005),
    ("KPI4 rule F1 (test)", 0.30, t["f1"], 0.005),
    ("Stock-out share in test rows (%)", 11.3, t["stockout_share_pct"], 0.05),
], columns=["check", "proposal_says", "script_result", "tolerance"])
# tolerance = half of the last digit written in the proposal (58 -> 0.5, 10.4 -> 0.05, 0.42 -> 0.005); counts must be equal
rec["match"] = np.where((rec["proposal_says"].astype(float) - rec["script_result"].astype(float)).abs() <= rec["tolerance"] + 1e-9, "OK", "DIFF")

def show_unknown(df):
    """Write the -1 code as the word Unknown in the sheets."""
    df = df.copy()
    df["categoryid"] = df["categoryid"].astype("int64").astype(object).where(df["categoryid"] != UNKNOWN_CAT, "Unknown")
    return df
cat_last, cat3, wl = show_unknown(cat_last), show_unknown(cat3), show_unknown(wl)

with pd.ExcelWriter(OUT_DIR / "G31-04 KPI Tables.xlsx") as xw:
    pd.DataFrame({"sheet": ["KPI1_OOS_rate", "KPI2_by_week", "KPI2_categories_latest", "KPI3_demand_unavail", "KPI3_by_category",
                            "KPI4_rule_by_week", "KPI4_rule_by_split", "Watchlist", "Reconcile",
                            "Data_dictionary", "Cleaning_log"],
                  "what": ["Out-of-stock rate of active items, each snapshot", "High-risk category count per prediction week (observed rate)",
                           "Categories for 6 to 13 Sep: observed stock-out rate, demand-weighted risk, tier",
                           "Share of views+add-to-carts that go to unavailable items, each snapshot",
                           "Same share by category, snapshot 13 Sep", "Simple rule baseline: TP/FP/FN/TN, recall, precision, F1 per week",
                           "Same, pooled per split (train/validate/test)", "Top 50 in-stock items with a recent status change by demand, 13 Sep",
                           "Script result vs the numbers written in the proposal",
                           "Columns we use: type, meaning, example, why (written by step 5)",
                           "Rows and columns before and after each cleaning step (written by step 5)"]}).to_excel(xw, sheet_name="README", index=False)
    k1.to_excel(xw, sheet_name="KPI1_OOS_rate", index=False); k2w.to_excel(xw, sheet_name="KPI2_by_week", index=False)
    cat_last.to_excel(xw, sheet_name="KPI2_categories_latest", index=False); k3.to_excel(xw, sheet_name="KPI3_demand_unavail", index=False)
    cat3.to_excel(xw, sheet_name="KPI3_by_category", index=False); k4.to_excel(xw, sheet_name="KPI4_rule_by_week", index=False)
    k4_split.reset_index().to_excel(xw, sheet_name="KPI4_rule_by_split", index=False); wl.to_excel(xw, sheet_name="Watchlist", index=False)
    rec.to_excel(xw, sheet_name="Reconcile", index=False)
print(rec.to_string(index=False))
