"""Step 2 (exploration): find the weekly snapshot dates of `available` and basic coverage."""
import pandas as pd
from config import WORK_DIR, DATA_DIR
p = pd.read_csv(WORK_DIR / "item_props_small.csv.gz", dtype={"value": "string"})
a = p[p.property == "available"].copy()
a["dt"] = pd.to_datetime(a["timestamp"], unit="ms")
a["day"] = a["dt"].dt.date
print("distinct timestamps:", a["timestamp"].nunique(), "| distinct days:", a["day"].nunique())
print(a.groupby("day").size().to_string())
print("values:", a["value"].value_counts().to_dict())
print("items with availability:", a["itemid"].nunique())
c = p[p.property == "categoryid"]
print("items with category:", c["itemid"].nunique(), "| categories:", c["value"].nunique())
e = pd.read_csv(WORK_DIR / "events_clean.csv.gz")   # duplicates removed in step 1
e["dt"] = pd.to_datetime(e["timestamp"], unit="ms")
print("events:", len(e), e["dt"].min(), e["dt"].max(), "| items:", e["itemid"].nunique(), "| visitors:", e["visitorid"].nunique())
print(e["event"].value_counts().to_dict())
