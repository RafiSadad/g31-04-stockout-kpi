"""Step 7: make every chart the group needs for slides and the report, from the outputs of steps 1 to 6.

Output: outputs/charts/*.png (1600 x 900 px, slide size). Every number in a chart is read from the run's own files:
work/cleaning_log.csv, work/modelling_table_features.csv.gz and outputs/G31-04 KPI Tables.xlsx. Nothing is typed by hand.

Charts
  01_cleaning_funnel.png      rows after each main cleaning step (explains 20M -> 2.3M -> ... -> modelling table)
  02_kpi_trend.png            KPI 1 (out-of-stock rate) and KPI 3 (demand on unavailable items) per weekly snapshot
  03_top_categories.png       categories with the highest observed stock-out rate, latest prediction week (KPI 2)
  04_target_balance.png       stock-out share per prediction week, with the train / validate / test split
  05_views_distribution.png   distribution of views in the last 7 days, and the stock-out rate per group
  06_feature_correlation.png  Spearman correlation of each feature with the target, train weeks only
  07_missing_values.png       share of empty values per column of the modelling table
Colors: validated categorical slots (blue #2a78d6, orange #eb6834) and the blue/red diverging pair; light surface.
"""
import re
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config import WORK_DIR, OUT_DIR
from cleanlog import PATH as LOG_PATH

CH = OUT_DIR / "charts"
CH.mkdir(parents=True, exist_ok=True)
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
BLUE, ORANGE, RED, BLUE_LIGHT, BAND = "#2a78d6", "#eb6834", "#e34948", "#86b6ef", "#f0efec"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "font.size": 12, "axes.titlesize": 17, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "legend.frameon": False,
})
SPLIT = lambda d: "train" if d <= "2015-07-26" else "validate" if d <= "2015-08-16" else "test"
made = []


def heading(fig, title, subtitle):
    """Title and subtitle anchored to the figure, so a wide label column never pushes them off the page."""
    fig.text(0.02, 0.955, title, fontsize=16, fontweight="bold", va="top")
    fig.text(0.02, 0.885, textwrap.fill(subtitle, 115), fontsize=9.5, color=INK2, va="top", linespacing=1.3)


def new(title, subtitle, left=0.1):
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
    fig.subplots_adjust(left=left, right=0.95, top=0.76, bottom=0.17)
    heading(fig, title, subtitle)
    return fig, ax


def save(fig, name, source):
    fig.text(0.01, 0.01, f"Source: {source}. Group G31-04, Dataset S1.", color=INK2, fontsize=8)
    fig.savefig(CH / name)
    plt.close(fig)
    made.append(name)


fmt = lambda v: f"{v:,.0f}"
log = pd.read_csv(LOG_PATH)
mt = pd.read_csv(WORK_DIR / "modelling_table_features.csv.gz")
x = pd.read_excel(OUT_DIR / "G31-04 KPI Tables.xlsx", sheet_name=None)


def rows_after(action_start):
    r = log[log["action"].str.startswith(action_start)]
    return int(r.iloc[-1]["rows_after"]) if len(r) else None


# ---------- 01 cleaning funnel ----------
note = log.loc[log["action"].str.startswith("stack part 1 and part 2"), "note"]
m = re.search(r"([\d,]+) different properties", str(note.iloc[-1])) if len(note) else None
steps = [("Raw item properties" + (f"\n(all {m.group(1)} properties)" if m else ""), rows_after("stack part 1 and part 2")),
         ("Keep available\nand categoryid", rows_after("keep property in")),
         ("Status: first record\nand changes only", rows_after("count first record")),
         ("One row per item\nper week (forward fill)", rows_after("item-weeks with a known status")),
         ("Modelling table: in stock,\nactive, with a label", len(mt))]
steps = [(n, v) for n, v in steps if v is not None]
fig, ax = new(f"From {steps[0][1]:,} raw rows to the modelling table",
              "Rows after each main step of the item data. The 4th bar is larger than the 3rd because the format changes "
              "to one row per item and week (the last known status is carried forward), not because data is added.", left=0.27)
labels, vals = zip(*steps)
y = np.arange(len(vals))[::-1]
ax.barh(y, vals, color=BLUE, height=0.55)
for yi, v in zip(y, vals):
    ax.text(v + max(vals) * 0.01, yi, fmt(v), va="center", fontsize=11)
ax.set_yticks(y, labels, fontsize=10)
ax.set_xlim(0, max(vals) * 1.15)
big = max(vals) >= 2e6
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1e6:.0f}M" if big else f"{v / 1e3:.0f}K"))
ax.grid(axis="y", visible=False)
save(fig, "01_cleaning_funnel.png", "work/cleaning_log.csv")

# ---------- 02 KPI trend ----------
k1, k3 = x["KPI1_OOS_rate"], x["KPI3_demand_unavail"]
d = pd.to_datetime(k1["snapshot"])
a1_, a2_ = k1["oos_rate_pct"], k3["demand_on_unavailable_pct"]
fig, ax = new(f"KPI 1 and KPI 3 per week: {a1_.iloc[0]:.1f}% to {a1_.iloc[-1]:.1f}% and {a2_.iloc[0]:.1f}% to {a2_.iloc[-1]:.1f}%",
              f"Each weekly snapshot, {k1['snapshot'].iloc[0]} to {k1['snapshot'].iloc[-1]} ({len(k1)} snapshots). Both values are percentages.")
for vals, col, name in [(k1["oos_rate_pct"], BLUE, "KPI 1: active items out of stock"),
                        (k3["demand_on_unavailable_pct"], ORANGE, "KPI 3: views and add-to-carts on unavailable items")]:
    ax.plot(d, vals, color=col, linewidth=2, marker="o", markersize=4, label=name)
    ax.annotate(f"{vals.iloc[-1]:.1f}%", (d.iloc[-1], vals.iloc[-1]), xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=10.5, color=INK)
ax.set_ylim(0, 75)
ax.set_ylabel("%")
ax.legend(loc="lower right", fontsize=10)
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d %b"))
save(fig, "02_kpi_trend.png", "outputs/G31-04 KPI Tables.xlsx, sheets KPI1_OOS_rate and KPI3_demand_unavail")

# ---------- 03 top categories ----------
c = x["KPI2_categories_latest"]
c = c[c["tier"].isin(["High", "Medium"])].head(15).iloc[::-1]
if len(c) == 0:
    print("skip 03_top_categories.png: no category has 20 or more eligible items")
else:
    wk = x["KPI2_by_week"].iloc[-1]
    fig, ax = new(f"High-risk categories: {int(wk['high_risk_categories'])} of {int(wk['eligible_categories'])}",
                  f"Observed stock-out rate, week {wk['snapshot']} to {wk['next_snapshot']}. Top 15 categories with at least 20 items.")
    cols = [BLUE if t == "High" else BLUE_LIGHT for t in c["tier"]]
    yy = np.arange(len(c))
    ax.barh(yy, c["observed_stockout_rate_pct"], color=cols, height=0.62)
    for yi, (v, n) in enumerate(zip(c["observed_stockout_rate_pct"], c["eligible_items"])):
        ax.text(v + 0.8, yi, f"{v:.1f}%  (n={n})", va="center", fontsize=9.5)
    ax.set_yticks(yy, [f"Cat {v}" for v in c["categoryid"]], fontsize=9.5)
    ax.set_xlim(0, c["observed_stockout_rate_pct"].max() * 1.25)
    ax.set_xlabel("% of eligible items out of stock the next week")
    ax.grid(axis="y", visible=False)
    handles = [matplotlib.patches.Patch(color=col, label=lab) for t, col, lab in
               [("High", BLUE, "High (top 10%)"), ("Medium", BLUE_LIGHT, "Medium (next 20%)")] if t in set(c["tier"])]
    ax.legend(handles=handles, loc="lower right", fontsize=10)
    save(fig, "03_top_categories.png", "outputs/G31-04 KPI Tables.xlsx, sheet KPI2_categories_latest")

# ---------- 04 target balance ----------
tb = mt.groupby("snapshot")["y_next_out"].agg(["mean", "size"]).reset_index()
tb["pct"] = 100 * tb["mean"]
overall = 100 * mt["y_next_out"].mean()
fig, ax = new(f"Target balance: {overall:.1f}% of rows run out of stock the next week",
              f"Stock-out share per prediction week ({len(tb)} weeks). A model that always says 'stays in stock' is {100 - overall:.0f}% right and useless.")
xx = np.arange(len(tb))
for split in ["train", "validate", "test"]:
    idx = [i for i, s in enumerate(tb["snapshot"]) if SPLIT(s) == split]
    ax.axvspan(idx[0] - 0.5, idx[-1] + 0.5, color=BAND if split != "validate" else SURFACE, zorder=0)
    ax.text((idx[0] + idx[-1]) / 2, 0.97, split, transform=ax.get_xaxis_transform(), ha="center", va="top",
            color=INK2, fontsize=10)
ax.bar(xx, tb["pct"], color=BLUE, width=0.62)
ax.axhline(overall, color=INK2, linewidth=1, linestyle="--", label=f"overall {overall:.1f}%")
ax.legend(loc="upper left", bbox_to_anchor=(0, 0.9), fontsize=9.5)
ax.set_ylim(0, tb["pct"].max() * 1.3)
for i in [int(tb["pct"].idxmax()), int(tb["pct"].idxmin())]:
    ax.text(i, tb["pct"][i] + 0.4, f"{tb['pct'][i]:.1f}%", ha="center", fontsize=9.5)
ax.set_xticks(xx, pd.to_datetime(tb["snapshot"]).dt.strftime("%d %b"), rotation=45, ha="right", fontsize=9)
ax.set_ylabel("% stock-outs")
ax.grid(axis="x", visible=False)
save(fig, "04_target_balance.png", "work/modelling_table_features.csv.gz")

# ---------- 05 views distribution ----------
bins = [-1, 0, 1, 2, 5, 10, 20, 50, np.inf]
names = ["0", "1", "2", "3-5", "6-10", "11-20", "21-50", "51+"]
g = mt.assign(b=pd.cut(mt["views_1w"], bins=bins, labels=names)).groupby("b", observed=False)["y_next_out"].agg(["size", "mean"])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 4.5), dpi=200, sharey=True)
fig.subplots_adjust(left=0.1, right=0.95, top=0.7, bottom=0.12, wspace=0.08)
heading(fig, "Views in the last 7 days and the stock-out rate",
        f"All {len(mt):,} rows of the modelling table, grouped by views in the 7 days before the snapshot. "
        f"Median views: {mt['views_1w'].median():.0f}; max: {mt['views_1w'].max():,.0f}.")
yy = np.arange(len(g))[::-1]
share = 100 * g["size"] / g["size"].sum()
a1.barh(yy, share, color=BLUE, height=0.62)
a2.barh(yy, 100 * g["mean"], color=ORANGE, height=0.62)
for a, vals, t in [(a1, share, "Share of rows (%)"), (a2, 100 * g["mean"], "Stock-out rate next week (%)")]:
    for yi, v in zip(yy, vals):
        a.text(v + vals.max() * 0.02, yi, f"{v:.1f}", va="center", fontsize=9.5)
    a.set_title(t, fontsize=11.5, loc="left", pad=4)
    a.set_xlim(0, vals.max() * 1.25)
    a.grid(axis="y", visible=False)
a1.set_yticks(yy, names)
a1.set_ylabel("Views in last 7 days")
save(fig, "05_views_distribution.png", "work/modelling_table_features.csv.gz")

# ---------- 06 feature correlation ----------
skip = {"itemid", "snapshot", "y_next_out", "state", "active", "cat", "parent_cat"}
feats = [f for f in mt.columns if f not in skip and pd.api.types.is_numeric_dtype(mt[f])]
tr = mt[mt["snapshot"].map(SPLIT) == "train"]
def spearman(a, b):
    """Spearman correlation = Pearson correlation of the ranks (no scipy needed). Rows with an empty value are left out."""
    ok = a.notna() & b.notna()
    return a[ok].rank().corr(b[ok].rank())
corr = pd.Series({f: spearman(tr[f], tr["y_next_out"]) for f in feats}).dropna()
corr = corr.reindex(corr.abs().sort_values().index)
fig, ax = new(f"Correlation of each feature with the target (largest |r| = {corr.abs().max():.3f})",
              f"Spearman correlation with 'out of stock next week', train weeks only ({len(tr):,} rows). "
              "Blue = positive, red = negative. Codes (cat, parent_cat) are left out.", left=0.26)
yy = np.arange(len(corr))
ax.barh(yy, corr.values, color=[BLUE if v >= 0 else RED for v in corr.values], height=0.62)
for yi, v in zip(yy, corr.values):
    off = corr.abs().max() * 0.03
    ax.text(v + (off if v >= 0 else -off), yi, f"{v:+.3f}", va="center", ha="left" if v >= 0 else "right", fontsize=8.5)
ax.set_yticks(yy, corr.index, fontsize=8.5)
ax.axvline(0, color=INK2, linewidth=0.8)
lim = corr.abs().max() * 1.35
ax.set_xlim(-lim, lim)
ax.grid(axis="y", visible=False)
save(fig, "06_feature_correlation.png", "work/modelling_table_features.csv.gz, train weeks 10 May to 26 Jul 2015")

# ---------- 07 missing values ----------
miss = (100 * mt.isna().mean()).sort_values()
miss = miss[miss > 0]
unknown = 100 * mt["cat_missing"].mean()
fig, ax = new("Missing values in the modelling table",
              f"Share of empty cells per column; columns with no empty cells are not shown. "
              f"Also: category 'Unknown' (code -1, not empty) in {unknown:.1f}% of rows.", left=0.28)
yy = np.arange(len(miss))
ax.barh(yy, miss.values, color=BLUE, height=0.5)
for yi, v in zip(yy, miss.values):
    ax.text(v + 1, yi, f"{v:.1f}%", va="center", fontsize=10.5)
ax.set_yticks(yy, miss.index)
ax.set_xlim(0, 100)
ax.set_xlabel("% of rows empty")
ax.grid(axis="y", visible=False)
save(fig, "07_missing_values.png", "work/modelling_table_features.csv.gz")

print(f"{len(made)} charts in {CH}:")
for m in made:
    print("  ", m)
