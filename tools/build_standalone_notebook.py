"""Build the standalone notebook notebooks/G31-04_Progress1_DataPrep.ipynb from the scripts in scripts/.

The notebook needs no GitHub and no access to anyone's Google Drive: all code is inside it. The code of every step is
copied from scripts/01_*.py ... scripts/07_*.py, so the notebook always computes exactly what the scripts compute.
Rerun this file after any change in scripts/:   python tools/build_standalone_notebook.py
"""
import ast
import base64
import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "scripts"
OUT = ROOT / "notebooks" / "G31-04_Progress1_DataPrep.ipynb"
RAW_LINK = "https://drive.google.com/drive/folders/1L2N2pFDTrI8cf2VQQMiS9PuqRIN0EuIq"
IMPORT_RE = re.compile(r"^from (config|cleanlog|dictionary_spec) import .*\n", re.M)
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell


def split_doc(path):
    """Return (docstring, code without the docstring and without the repository imports)."""
    text = path.read_text()
    tree = ast.parse(text)
    doc = ast.get_docstring(tree) or ""
    if doc:
        end = tree.body[0].end_lineno
        text = "\n".join(text.splitlines()[end:]).lstrip("\n") + "\n"
    return doc, IMPORT_RE.sub("", text)


def parts(text):
    """Split code at top-level '# ----------' comments, so long steps become several readable cells."""
    chunks, cur = [], []
    for line in text.splitlines():
        if line.startswith("# ----------") and any(l.strip() for l in cur):
            chunks.append("\n".join(cur).strip("\n"))
            cur = []
        cur.append(line)
    chunks.append("\n".join(cur).strip("\n"))
    return [c for c in chunks if c.strip()]


cells = []
cells.append(md("""# G31-04 Stock-Out Risk Prediction: data preparation (Progress 1)
Group G31-04, Dataset S1 (e-commerce events and item properties, 3 May to 18 Sep 2015).
Data Engineer part: cleaning, weekly item table with the target, category fixes, demand features, data dictionary,
cleaning log, KPI tables and all charts.

**This notebook is standalone.** All code is inside. It needs only the 4 raw CSV files of Dataset S1:
`item_properties_part1.csv`, `item_properties_part2.csv`, `events.csv`, `category_tree.csv`.

**How to run (Google Colab or Jupyter)**
1. In cell 1, choose how to give the 4 raw files:
   - `download` (default): downloads them from the group's public Google Drive folder. No sign-in needed.
   - `upload`: Colab shows a button to pick the files (or one zip) from your computer.
   - `folder`: the files are already in a folder (type its path in `RAW_FOLDER`). In Colab you can also drag the 4 files
     into the folder `G31-04_run/data_raw` in the *Files* panel on the left; they are then used directly.
2. *Runtime > Run all* (Colab) or *Run > Run All Cells* (Jupyter). A full run takes about 5 to 10 minutes and about 4 GB RAM.
3. All results are in the folder `G31-04_run` and in `G31-04_Progress1_results.zip` (downloaded at the end in Colab).

Every number below is computed by this code. Nothing is typed by hand, except the numbers from the proposal and the
Progress 1 slides that the results are compared with (they are marked as such)."""))

cells.append(code('''#@title 0. Setup: folders and libraries
import os, sys, glob, shutil, zipfile, subprocess, importlib.util, gc
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
RUN_DIR = Path(os.environ.get("NB_RUN_DIR", "/content/G31-04_run" if IN_COLAB else "G31-04_run")).resolve()
DATA_DIR, WORK_DIR, OUT_DIR, DOCS_DIR = RUN_DIR / "data_raw", RUN_DIR / "work", RUN_DIR / "outputs", RUN_DIR / "docs"
for d in (DATA_DIR, WORK_DIR, OUT_DIR, DOCS_DIR):
    d.mkdir(parents=True, exist_ok=True)
os.chdir(RUN_DIR)
UNKNOWN_CAT = -1   # code for the "Unknown" category (no categoryid known at or before the snapshot)

missing = [m for m in ["pandas", "numpy", "openpyxl", "matplotlib", "gdown"] if importlib.util.find_spec(m) is None]
if missing:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", *missing], check=True)
import pandas, numpy, matplotlib, openpyxl
print("run folder:", RUN_DIR)
print("python", sys.version.split()[0], "| pandas", pandas.__version__, "| numpy", numpy.__version__,
      "| matplotlib", matplotlib.__version__, "| openpyxl", openpyxl.__version__)


def _free(before):
    """Forget the variables a step made (as if every step were a new program) and free the memory."""
    for k in list(globals()):
        if k not in before and not k.startswith("_") and k not in ("In", "Out"):
            del globals()[k]
    gc.collect()'''))

doc, cl = split_doc(S / "cleanlog.py")
cells.append(code("#@title 0b. Cleaning log helper (rows and columns before and after each step)\n" + cl.strip()
                  + "\n\nLOG_PATH = PATH"))
doc, spec = split_doc(S / "dictionary_spec.py")
cells.append(code("#@title 0c. Data dictionary text: type, meaning, used, why (example values come from the data in step 5)\n"
                  + spec.strip()))

cells.append(md("## 1. The raw data"))
cells.append(code(f'''#@title 1. Get the 4 raw CSV files
RAW_SOURCE = "download"  #@param ["download", "upload", "folder"]
DOWNLOAD_LINK = "{RAW_LINK}"  #@param {{type:"string"}}
RAW_FOLDER = ""  #@param {{type:"string"}}
RAW_SOURCE = os.environ.get("NB_RAW_SOURCE", RAW_SOURCE)     # only for testing outside Colab
RAW_FOLDER = os.environ.get("NB_RAW_FOLDER", RAW_FOLDER)

NEEDED = ["item_properties_part1.csv", "item_properties_part2.csv", "events.csv", "category_tree.csv"]
have = lambda: [n for n in NEEDED if (DATA_DIR / n).exists()]


def collect(src):
    """Copy the 4 CSVs from a folder (any sub-folder) into data_raw/, or extract them from a zip there."""
    for name in NEEDED:
        if (DATA_DIR / name).exists():
            continue
        hits = glob.glob(f"{{src}}/**/{{name}}", recursive=True)
        if hits:
            shutil.copy(hits[0], DATA_DIR / name)
            continue
        for z in glob.glob(f"{{src}}/**/*.zip", recursive=True):
            with zipfile.ZipFile(z) as zf:
                member = next((m for m in zf.namelist() if m.endswith(name)), None)
                if member:
                    with zf.open(member) as s, open(DATA_DIR / name, "wb") as d:
                        shutil.copyfileobj(s, d)
                    break


if len(have()) < len(NEEDED):
    if RAW_SOURCE == "download":
        import gdown
        tmp = RUN_DIR / "download"
        if "/folders/" in DOWNLOAD_LINK:
            gdown.download_folder(url=DOWNLOAD_LINK, output=str(tmp), quiet=False, use_cookies=False)
        else:   # a link to one file, for example the course zip
            tmp.mkdir(exist_ok=True)
            gdown.download(url=DOWNLOAD_LINK, output=str(tmp / "raw_download.zip"), quiet=False, fuzzy=True)
        collect(tmp)
    elif RAW_SOURCE == "upload":
        if not IN_COLAB:
            raise RuntimeError(f"Upload works in Colab only. Copy the 4 files into {{DATA_DIR}} and run this cell again.")
        from google.colab import files
        up = RUN_DIR / "upload"
        up.mkdir(exist_ok=True)
        for name, data in files.upload().items():   # pick the 4 CSV files, or one zip with them
            (up / name).write_bytes(data)
        collect(up)
    else:
        collect(RAW_FOLDER)

miss = [n for n in NEEDED if n not in have()]
if miss:
    raise FileNotFoundError(f"Missing raw files: {{miss}}. Check RAW_SOURCE, DOWNLOAD_LINK or RAW_FOLDER in this cell.")
for n in NEEDED:
    print(f"{{n:28s}} {{(DATA_DIR / n).stat().st_size:>13,}} bytes")'''))

cells.append(code('''#@title 1b. A first look: column names and the first 3 rows of each raw file
from IPython.display import display
for n in NEEDED:
    print(n)
    display(pandas.read_csv(DATA_DIR / n, nrows=3))'''))

STEPS = [
    ("01_extract_raw", "Step 1: read the raw files and first cleaning",
     "Keeps only the 2 readable item properties (`available`, `categoryid`) out of all properties, and removes exact duplicate events."),
    ("02_explore_snapshots", "Step 2: check the weekly snapshot dates",
     "Prints the dates on which `available` was recorded, and basic counts. Nothing is saved."),
    ("03_build_kpis", "Step 3: weekly item table, target, category fixes, KPI tables",
     "One row per item and week, status carried forward, the target (out of stock 7 days later), the 'Unknown' and parent "
     "category, the 4 KPI tables, and the check against the numbers written in the proposal (Reconcile)."),
    ("04_demand_features", "Step 4: demand features", "Adds the demand features to the modelling table. Only data at or before the snapshot is used."),
    ("05_docs", "Step 5: data dictionary and cleaning log", "Writes the data dictionary (with real example values) and the cleaning log."),
    ("06_export_compare", "Step 6: cleaned dataset (CSV) and comparison with the Progress 1 slides",
     "Writes the cleaned modelling table as CSV for the submission, and puts our counts next to the numbers on the Progress 1 slides."),
    ("07_charts", "Step 7: all charts and pictures of the data",
     "Every chart for the slides and the report, and a picture of each raw file and the modelling table (header and first real rows)."),
]
cells.append(md("## 2. The pipeline (steps 1 to 7)\nEach step reads what the step before saved in `G31-04_run/`, so the steps can be checked one by one."))
for name, title, what in STEPS:
    doc, body = split_doc(S / f"{name}.py")
    cells.append(md(f"### {title}\n{what}\n\n```text\n{doc}\n```\n*Code copied from `scripts/{name}.py`.*"))
    chunks = parts(body)
    for i, ch in enumerate(chunks):
        head = f"#@title {title}" + (f" (part {i + 1} of {len(chunks)})" if len(chunks) > 1 else "")
        pre = "_before = set(globals())\n" if i == 0 else ""
        post = "\n_free(_before)" if i == len(chunks) - 1 else ""
        cells.append(code(f"{head}\n{pre}{ch}{post}"))

cells.append(md("## 3. Results"))
cells.append(code('''#@title Cleaning log: rows and columns before and after each step
import pandas as pd
pd.set_option("display.max_colwidth", 140)
pd.read_csv(LOG_PATH)[["script", "step", "action", "rows_before", "cols_before", "rows_after", "cols_after", "note"]]'''))
cells.append(code('''#@title Reconcile: our results vs the numbers written in the proposal (OK = same within the proposal's rounding)
pd.read_excel(OUT_DIR / "G31-04 KPI Tables.xlsx", sheet_name="Reconcile")'''))
cells.append(code('''#@title Our counts vs the numbers on the Progress 1 slides
pd.read_csv(OUT_DIR / "compare_progress1.csv")'''))
cells.append(code('''#@title Modelling table: size, target balance, first rows, summary of every column
mt = pd.read_csv(WORK_DIR / "modelling_table_features.csv.gz")
print(f"{len(mt):,} rows x {mt.shape[1]} columns | stock-outs next week: {int(mt.y_next_out.sum()):,} ({100 * mt.y_next_out.mean():.1f}%)")
display(mt.head())
mt.describe().T[["count", "mean", "50%", "max"]].round(3)'''))
cells.append(code('''#@title Data dictionary (also in G31-04_run/docs/data_dictionary.md and in the Excel file)
pd.read_excel(OUT_DIR / "G31-04 KPI Tables.xlsx", sheet_name="Data_dictionary")'''))
cells.append(code('''#@title All charts (files in G31-04_run/outputs/charts)
from IPython.display import Image
for f in sorted(glob.glob(str(OUT_DIR / "charts" / "*.png"))):
    print(Path(f).name)
    display(Image(f, width=1000))'''))
flow = base64.b64encode((ROOT / "docs" / "data_flow.png").read_bytes()).decode()
cells.append(code("#@title Data flow diagram (drawn by the group; picture stored inside this notebook)\n"
                  "import base64\nfrom IPython.display import Image\n"
                  f"display(Image(data=base64.b64decode(\"{flow}\"), width=1100))"))
cells.append(code('''#@title Save everything as one zip (Colab downloads it to your computer)
zip_path = RUN_DIR / "G31-04_Progress1_results.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for folder in (OUT_DIR, DOCS_DIR):
        for f in sorted(folder.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(RUN_DIR))
    z.write(LOG_PATH, LOG_PATH.relative_to(RUN_DIR))
names = zipfile.ZipFile(zip_path).namelist()
print(f"{zip_path} ({zip_path.stat().st_size / 1e6:.1f} MB, {len(names)} files)")
for n in names:
    print("  ", n)
if IN_COLAB:
    from google.colab import files
    files.download(str(zip_path))'''))

nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"},
               "colab": {"provenance": [], "toc_visible": True}}
OUT.parent.mkdir(exist_ok=True)
nbf.write(nb, OUT)
print(f"wrote {OUT.relative_to(ROOT)} ({len(cells)} cells, {OUT.stat().st_size / 1e3:.0f} KB)")
