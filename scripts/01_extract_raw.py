"""Step 1: read the raw files and do the first cleaning.

a) item_properties part 1 and 2: keep only property in {available, categoryid}. Read in chunks so RAM stays low.
   Output: work/item_props_small.csv.gz
b) events.csv: remove exact duplicate rows (same values in all 5 columns). Output: work/events_clean.csv.gz
   All later steps read the cleaned events, never the raw file.
Step 1 also starts a new cleaning log (work/cleaning_log.csv), so every full run gives one clean log.
"""
import pandas as pd
from config import DATA_DIR, WORK_DIR
from cleanlog import CleanLog, PATH as LOG_PATH

LOG_PATH.unlink(missing_ok=True)          # new run, new log
log = CleanLog("01_extract_raw")

# ---------- a) item properties ----------
KEEP = {"available", "categoryid"}
parts, n_raw, n_cols, props = [], 0, 0, set()
for name in ("item_properties_part1.csv", "item_properties_part2.csv"):
    total = 0
    for ch in pd.read_csv(DATA_DIR / name, chunksize=2_000_000,
                          dtype={"timestamp": "int64", "itemid": "int64", "property": "string", "value": "string"}):
        total += len(ch)
        n_cols = ch.shape[1]
        props.update(ch["property"].unique())
        parts.append(ch[ch["property"].isin(KEEP)])
    print(name, "rows read:", total, flush=True)
    log.add("read raw file", name, (0, 0), (total, n_cols), "chunks of 2,000,000 rows")
    n_raw += total
df = pd.concat(parts, ignore_index=True)
log.add("stack part 1 and part 2", "item_properties (both parts)", (n_raw, n_cols), (n_raw, n_cols),
        f"long format: one row = one property value of one item at one time; {len(props):,} different properties")
log.add("keep property in {available, categoryid}", "item_properties -> item_props_small", (n_raw, n_cols), df.shape,
        f"the other {len(props) - len(KEEP):,} properties have coded names and values; "
        + ", ".join(f"{k}: {v:,}" for k, v in df["property"].value_counts().items()))
df.to_csv(WORK_DIR / "item_props_small.csv.gz", index=False)
print("kept rows:", len(df), "| properties in raw data:", len(props))

# ---------- b) events ----------
ev = pd.read_csv(DATA_DIR / "events.csv")
log.add("read raw file", "events.csv", (0, 0), ev.shape)
n0 = ev.shape
ev = ev.drop_duplicates(ignore_index=True)
log.add("drop exact duplicate events (all 5 columns equal)", "events -> events_clean", n0, ev.shape,
        f"{n0[0] - len(ev):,} duplicate rows removed (keep the first)")
ev.to_csv(WORK_DIR / "events_clean.csv.gz", index=False)
print("events:", n0[0], "->", len(ev))
