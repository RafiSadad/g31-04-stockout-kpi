"""Step 1: keep only property in {available, categoryid} from the two big item_properties files.
Reads in chunks so RAM stays low. Output: work/item_props_small.csv.gz"""
import pandas as pd
from config import DATA_DIR, WORK_DIR
from cleanlog import CleanLog

log = CleanLog("01_extract_properties")
KEEP = {"available", "categoryid"}
parts, n_raw, n_cols = [], 0, 0
for name in ("item_properties_part1.csv", "item_properties_part2.csv"):
    total = 0
    for ch in pd.read_csv(DATA_DIR / name, chunksize=2_000_000,
                          dtype={"timestamp": "int64", "itemid": "int64", "property": "string", "value": "string"}):
        total += len(ch)
        n_cols = ch.shape[1]
        parts.append(ch[ch["property"].isin(KEEP)])
    print(name, "rows read:", total, flush=True)
    log.add("read raw file", name, (0, 0), (total, n_cols), "chunks of 2,000,000 rows")
    n_raw += total
df = pd.concat(parts, ignore_index=True)
log.add("stack part 1 and part 2", "item_properties (both parts)", (n_raw, n_cols), (n_raw, n_cols), "no rows dropped")
log.add("keep property in {available, categoryid}", "item_properties -> item_props_small", (n_raw, n_cols), df.shape,
        "other properties are hashed and not used; "
        + ", ".join(f"{k}: {v:,}" for k, v in df["property"].value_counts().items()))
df.to_csv(WORK_DIR / "item_props_small.csv.gz", index=False)
print("kept rows:", len(df), "| by property:\n", df["property"].value_counts().to_string())
