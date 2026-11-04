# Project context

Group G31-04, Dataset S1 (Retailrocket-style e-commerce data, 3 May to 18 Sep 2015).
Project: Stock-Out Risk Prediction. Predict whether an in-stock, active item runs out of stock
next week, and summarize it as a risk score per category for a Head of Inventory.
I am Rafi (Data Engineer). My tasks: data dictionary, demand features, missing category values,
cleaning log, data flow diagram.

# Read first

1. README.md and LOG.md (definitions, steps, how to rerun, known issues).
2. outputs/G31-04 KPI Tables.xlsx, sheet Reconcile (numbers that must still match the proposal).

# Rules

- Raw data is in data_raw/ and never committed. Do not print or read whole big CSVs, use scripts.
- Do the work with scripts in scripts/ (numbered, rerunnable), not by hand.
- Keep the definitions in LOG.md section 3. If a change is needed, say so and update LOG.md.
- After every change, rerun scripts and check the Reconcile sheet. Report any DIFF.
- Never invent numbers or sources. If something is unclear, ask me.
- Update LOG.md after each task: what was done, which code and libraries, how to rerun, what can fail.
- Write in simple English. No em dashes. Plain academic style.
- Small commits with clear messages. Do not push to main without telling me.
