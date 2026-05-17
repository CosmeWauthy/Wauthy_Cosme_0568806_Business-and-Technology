## FAIR LOG

Date: 2026-05-13
Tool: Codex
Model: GPT-5
Purpose: Run preliminary diagnostics and ADF/KPSS stationarity testing on the three core monthly log variables.

### Prompt

Continue the master thesis project from the existing local and Google Drive setup. Read the project handoff/wiki files first, then run preliminary diagnostics and stationarity testing on `log_bitcoin_market_price_usd`, `log_mci_weighted`, and `log_mci_frontier` in `monthly_master_panel.csv`. Inspect levels and first differences, run ADF and KPSS on levels and first differences, and only move to Johansen testing after I confirm whether the variables are plausibly `I(1)`.

### Output (condensed)

Read the project handoff, task tracker, data/model/econometrics/decision wiki files, the monthly master-panel audit, and the relevant construction scripts. Created `scripts/11_preliminary_diagnostics.py`, installed the missing standard econometrics dependencies in the local virtual environment (`statsmodels`, `scipy`, `patsy`, and `tabulate`), and ran the diagnostics on the 2010-08 to 2025-12 sample. Wrote CSV tables, a Markdown diagnostics report, and a levels/first-differences figure. Results: `log_mci_frontier` is plausibly `I(1)`, while `log_bitcoin_market_price_usd` and `log_mci_weighted` show ambiguous evidence that should be checked before Johansen testing.

### Usage

Used.

This interaction documents the first econometric diagnostics step and supports the decision not to proceed mechanically to Johansen testing until the integration-order ambiguity is resolved.

### Reference

File name: 2026-05-13_preliminary-stationarity-diagnostics.md
