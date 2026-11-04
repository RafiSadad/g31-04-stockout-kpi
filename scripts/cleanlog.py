"""Cleaning log helper. Every script records row and column counts before and after each step.

Rows go to work/cleaning_log.csv. Each script first removes its own old rows, so a rerun does not
duplicate them. Step 5 (05_docs.py) turns the file into outputs/cleaning_log.csv, docs/cleaning_log.md
and the sheet Cleaning_log in the KPI workbook.
"""
import pandas as pd
from config import WORK_DIR

PATH = WORK_DIR / "cleaning_log.csv"
COLS = ["script", "step", "action", "table", "rows_before", "cols_before", "rows_after", "cols_after",
        "rows_changed", "note"]


class CleanLog:
    def __init__(self, script):
        self.script = script
        self.n = 0
        old = pd.read_csv(PATH) if PATH.exists() else pd.DataFrame(columns=COLS)
        self.rows = old[old["script"] != script].to_dict("records")
        self._save()

    def add(self, action, table, before, after, note=""):
        """before and after are (rows, cols) tuples."""
        self.n += 1
        rb, cb = before
        ra, ca = after
        self.rows.append({"script": self.script, "step": self.n, "action": action, "table": table,
                          "rows_before": int(rb), "cols_before": int(cb), "rows_after": int(ra), "cols_after": int(ca),
                          "rows_changed": int(ra) - int(rb), "note": note})
        print(f"[log] {action}: {table} {rb:,} x {cb} -> {ra:,} x {ca}. {note}", flush=True)
        self._save()

    def _save(self):
        df = pd.DataFrame(self.rows, columns=COLS)
        df["order"] = df["script"].str[:2]
        df.sort_values(["order", "step"], kind="stable").drop(columns="order").to_csv(PATH, index=False)
