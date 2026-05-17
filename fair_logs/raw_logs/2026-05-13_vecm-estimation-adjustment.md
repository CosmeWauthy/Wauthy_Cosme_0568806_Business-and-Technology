# FAIR Raw Log: VECM Estimation and Adjustment Coefficients

## Metadata

- Date: 2026-05-13
- Tool / model: Codex / GPT-5
- Project: Master thesis Bitcoin marginal-cost analysis
- Location: local code folder plus Google Drive thesis project root

## Prompt Summary

The user asked to continue the master thesis project from existing local and Google Drive context, preserve the established integration-order and cointegration interpretation, and proceed to VECM estimation and adjustment-coefficient interpretation from the documented rank-1 candidate systems.

## Actions Taken

- Read the project handoff, task list, econometrics, data, model, and decisions wiki files.
- Read the latest stationarity, Johansen, and Gregory-Hansen output reports.
- Created `scripts/15_vecm_estimation.py`.
- Estimated four labeled rank-1 VECM candidates:
  - primary frontier ASIC-era constant specification;
  - weighted full-sample parsimonious constant specification;
  - frontier full-sample no-deterministic sensitivity;
  - weighted ASIC-era restricted-trend sensitivity.
- Wrote reproducible VECM outputs to `outputs/tables`.
- Updated `wiki/econometrics.md`, `wiki/next_session_handoff.md`, and `wiki/Tasks.md`.

## Outputs Created

- `outputs/tables/vecm_specifications.csv`
- `outputs/tables/vecm_cointegrating_relations.csv`
- `outputs/tables/vecm_adjustment_coefficients.csv`
- `outputs/tables/vecm_short_run_coefficients.csv`
- `outputs/tables/vecm_residual_diagnostics.csv`
- `outputs/tables/vecm_estimation_report.md`

## Thesis Use

Use these results for the adjustment-coefficient section of the econometric analysis. The safest thesis interpretation is that the strongest standard VECM evidence points to clearer adjustment in the constructed frontier marginal-cost index than in Bitcoin price, but the relationship is unstable and requires rolling-window VECM analysis.
