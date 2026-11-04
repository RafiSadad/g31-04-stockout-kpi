"""Step 1: keep only property in {available, categoryid} from the two big item_properties files.
Reads in chunks so RAM stays low. Output: work/item_props_small.csv.gz"""
import pandas as pd
from config import DATA_DIR, WORK_DIR

KEEP = {"available", "categoryid"}
parts = []
for name in ("item_properties_part1.csv", "item_properties_part2.csv"):
    total = 0
    for ch in pd.read_csv(DATA_DIR / name, chunksize=2_000_000,
                          dtype={"timestamp": "int64", "itemid": "int64", "property": "string", "value": "string"}):
        total += len(ch)
        parts.append(ch[ch["property"].isin(KEEP)])
    print(name, "rows read:", total, flush=True)
df = pd.concat(parts, ignore_index=True)
df.to_csv(WORK_DIR / "item_props_small.csv.gz", index=False)
print("kept rows:", len(df), "| by property:\n", df["property"].value_counts().to_string())
