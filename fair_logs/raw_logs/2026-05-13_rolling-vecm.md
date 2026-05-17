# FAIR Raw Log: Rolling-Window VECM

## Metadata

- Date: 2026-05-13
- Tool / model: Codex / GPT-5
- Project: Master thesis Bitcoin marginal-cost analysis

## Prompt Summary

The user asked to proceed with rolling VECM estimation and to account for what previous tests revealed when interpreting the results.

## Actions Taken

- Created `scripts/17_rolling_vecm.py`.
- Estimated rolling rank-1 VECMs using `48`-month and `36`-month windows.
- Treated the frontier ASIC-era restricted-constant model as the main system, following prior Johansen, Gregory-Hansen, and static VECM evidence.
- Included weighted and full-sample systems only as robustness/sensitivity checks.
- Wrote rolling coefficient, summary, regime-summary, report, and figure outputs.
- Updated `wiki/econometrics.md`, `wiki/next_session_handoff.md`, and `wiki/Tasks.md`.

## Outputs Created

- `outputs/tables/rolling_vecm_coefficients.csv`
- `outputs/tables/rolling_vecm_summary.csv`
- `outputs/tables/rolling_vecm_regime_summary.csv`
- `outputs/tables/rolling_vecm_report.md`
- `outputs/figures/rolling_vecm_frontier_asic_adjustment.png`

## Thesis Use

Use these results to support the conclusion that frontier MCI adjustment is recurrent but not stable. This reinforces the static VECM and Gregory-Hansen interpretation: the price-cost relation is structurally unstable, and marginal cost is better interpreted as endogenous to mining-market conditions than as a fixed exogenous price anchor.
