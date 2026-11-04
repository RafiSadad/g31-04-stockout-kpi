"""Step 4: add demand features to the modelling table.

Input : work/modelling_table.csv.gz and work/item_week.csv.gz (step 3), work/item_props_small.csv.gz (step 1, for the
        exact snapshot timestamps), data_raw/events.csv (for visitors and the time of the last purchase).
Output: work/modelling_table_features.csv.gz (same rows as the modelling table, more columns).

Every feature uses only events at or before the snapshot time t, so nothing from the label week leaks in.
Windows: 1w = (t - 7 days, t], 4w = (t - 28 days, t]. The reason for each feature is in docs/data_dictionary.md.
"""
import numpy as np
import pandas as pd
from config import DATA_DIR, WORK_DIR, UNKNOWN_CAT
from cleanlog import CleanLog

DAY = 86_400_000
log = CleanLog("04_demand_features")
mt = pd.read_csv(WORK_DIR / "modelling_table.csv.gz")
log.add("load modelling table", "modelling_table", (0, 0), mt.shape)
shape_in = mt.shape

# exact snapshot timestamp for each snapshot date
p = pd.read_csv(WORK_DIR / "item_props_small.csv.gz", usecols=["timestamp", "property"])
snaps = np.sort(p.loc[p["property"] == "available", "timestamp"].unique())
t_of = dict(zip(pd.to_datetime(snaps, unit="ms").strftime("%Y-%m-%d"), snaps))
del p
ev = pd.read_csv(DATA_DIR / "events.csv", usecols=["timestamp", "visitorid", "event", "itemid"])
log.add("load events (4 of 5 columns)", "events", (0, 0), ev.shape, "transactionid not needed")

# ---------- features from columns that step 3 already made ----------
mt["demand_4w"] = mt["views_4w"] + mt["atc_4w"]
mt["demand_prev3w_avg"] = (mt["demand_4w"] - mt["demand_1w"]) / 3
mt["demand_trend"] = (mt["demand_1w"] + 1) / (mt["demand_prev3w_avg"] + 1)
mt["atc_rate_1w"] = np.where(mt["views_1w"] > 0, mt["atc_1w"] / mt["views_1w"].where(mt["views_1w"] > 0), 0.0)
mt["buy_rate_4w"] = np.where(mt["views_4w"] > 0, mt["tx_4w"] / mt["views_4w"].where(mt["views_4w"] > 0), 0.0)

# ---------- features that need the events again ----------
vis, last_tx = [], []
weeks = set(mt["snapshot"])
for d, t in t_of.items():
    if d not in weeks:
        continue
    w = ev[(ev["timestamp"] > t - 7 * DAY) & (ev["timestamp"] <= t) & ev["event"].isin(["view", "addtocart"])]
    vis.append(w.groupby("itemid")["visitorid"].nunique().rename("visitors_1w").reset_index().assign(snapshot=d))
    tx = ev[(ev["timestamp"] <= t) & (ev["event"] == "transaction")]
    lt = tx.groupby("itemid")["timestamp"].max()
    last_tx.append(((t - lt) / DAY).round(2).rename("days_since_last_tx").reset_index().assign(snapshot=d))
mt = mt.merge(pd.concat(vis), on=["itemid", "snapshot"], how="left")
mt["visitors_1w"] = mt["visitors_1w"].fillna(0).astype(int)
mt = mt.merge(pd.concat(last_tx), on=["itemid", "snapshot"], how="left")   # empty = no purchase seen before t

# ---------- category demand (all active items of the category, in stock or not) ----------
iw = pd.read_csv(WORK_DIR / "item_week.csv.gz")
cd = iw[iw["cat"] != UNKNOWN_CAT].groupby(["snapshot", "cat"])["demand_1w"].sum().rename("cat_demand_1w").reset_index()
mt = mt.merge(cd, on=["snapshot", "cat"], how="left")                       # empty for Unknown category
mt["item_share_of_cat_demand"] = np.where(mt["cat_demand_1w"] > 0, mt["demand_1w"] / mt["cat_demand_1w"], np.nan)

# ---------- checks ----------
assert len(mt) == shape_in[0], "row count changed"
assert not mt.duplicated(["itemid", "snapshot"]).any(), "duplicate item-week rows"
new = [c for c in mt.columns if c not in pd.read_csv(WORK_DIR / "modelling_table.csv.gz", nrows=0).columns]
log.add("add demand features", "modelling_table -> modelling_table_features", shape_in, mt.shape,
        f"{len(new)} new columns: " + ", ".join(new))
mt.to_csv(WORK_DIR / "modelling_table_features.csv.gz", index=False)
print("\nFeature summary (all rows):")
print(mt[new].describe().T[["count", "mean", "50%", "max"]].round(3).to_string())
print("\nRows with empty days_since_last_tx:", int(mt["days_since_last_tx"].isna().sum()),
      "| rows with empty cat_demand_1w (Unknown category):", int(mt["cat_demand_1w"].isna().sum()))
