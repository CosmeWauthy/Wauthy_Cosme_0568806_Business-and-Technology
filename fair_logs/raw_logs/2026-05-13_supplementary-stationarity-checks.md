## FAIR LOG

Date: 2026-05-13
Tool: Codex
Model: GPT-5
Purpose: Run supplementary stationarity checks after preliminary ADF/KPSS diagnostics.

### Prompt

User asked to move on to supplementary stationarity checking: alternate KPSS bandwidth/lag choices, Zivot-Andrews break-aware unit-root tests, and possibly later-start sample sensitivity.

### Output (condensed)

Created and ran `scripts/12_supplementary_stationarity_checks.py`. The script writes KPSS lag/bandwidth sensitivity tables, Zivot-Andrews break-aware unit-root test results, later-start sample sensitivity tables, and a Markdown summary report. Results show that the first-difference KPSS rejection for `log_mci_weighted` is bandwidth-fragile, supporting the lifecycle-rule interpretation rather than clear `I(2)` behavior. `log_mci_frontier` remains broadly consistent with `I(1)`. `log_bitcoin_market_price_usd` is mostly `I(1)` under later-start checks, but Zivot-Andrews rejects the unit-root null in levels, indicating important break-sensitive price dynamics.

### Usage

Used.

This interaction supports the decision to proceed to conventional Johansen testing with explicit caveats about approximate `I(1)` evidence and structural-break robustness.

### Reference

File name: 2026-05-13_supplementary-stationarity-checks.md
