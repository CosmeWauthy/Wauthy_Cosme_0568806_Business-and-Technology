## FAIR LOG

Date: 2026-05-12
Tool: Codex
Model: GPT-5
Purpose: Construct and document the monthly weighted-average hardware-efficiency path from the cleaned CCAF/CBECI hardware master table.

### Prompt

User provided detailed construction instructions for the weighted-average hardware efficiency path, including a two-month deployment lag, monthly grid, 60-month active lifetime, straight-line depreciation weights, weighted-average efficiency formula, output columns, and validation checks. User requested: Make sure to document this.

### Output (condensed)

Created `scripts/09_construct_weighted_efficiency.py`. The script reads `backbone_monthly.csv` and `hardware_master_clean.csv`, computes deployment month as release month plus two months, keeps devices active for 60 months, assigns depreciation weights by active-year bucket, and computes `eta_weighted_avg` as a weighted mean of `efficiency_j_per_th`. It writes `weighted_efficiency_monthly.csv`, `weighted_efficiency_monthly_audit.csv`, and `weighted_efficiency_monthly_audit.md`. The audit reports 202 rows, no missing weighted-efficiency months, no zero-active-device months, no first-year weight mismatches, and one accepted sustained increase run from 2015-08 to 2015-10. Updated wiki documentation and task/model status.

### Usage

Used.

This interaction creates and documents the lifecycle-weighted hardware-efficiency path needed for the weighted marginal-cost index in the thesis.

### Reference

File name: 2026-05-12_weighted-efficiency-path.md
