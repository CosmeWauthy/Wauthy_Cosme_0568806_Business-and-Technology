# Reproducibility Notes

## Workflow Order

The main workflow is numbered by script prefix.

1. `scripts/analysis/01_prepare_data.py`: cleans raw price, Coin Metrics, difficulty, and subsidy-validation files.
2. `scripts/analysis/02_prepare_hardware.py`: cleans the CCAF/CBECI hardware list.
3. `scripts/analysis/03_aggregate_monthly_backbone.py`: aggregates the daily backbone to monthly frequency.
4. `scripts/analysis/04_construct_frontier_efficiency.py`: constructs the frontier efficiency path.
5. `scripts/analysis/05_construct_weighted_efficiency.py`: constructs the weighted-average efficiency path.
6. `scripts/analysis/06_construct_monthly_master_panel.py`: combines the monthly backbone and efficiency paths into the final analysis panel.
7. `scripts/analysis/07_preliminary_diagnostics.py` through `scripts/analysis/14_weak_exogeneity_tests.R`: run stationarity, cointegration, VECM, rolling-window, and weak-exogeneity analyses.
8. `scripts/figures/01_plot_bitcoin_price_events.R` through `scripts/figures/03_generate_appendix_b_figures.R`: generate the final thesis and appendix figures.

## Included Processed Data

The repository includes the final processed monthly analysis panel:

- `data/processed/monthly/monthly_master_panel.csv`

This file makes the final econometric workflow inspectable and rerunnable without redistributing raw downloads. It is derived from the sources documented in `data/raw/README.md`.

## Path Configuration

Python scripts read `config/paths.yaml`. R scripts use the repository root by default and may also be pointed at another root with:

```bash
export THESIS_ANALYSIS_ROOT=/path/to/repo
```
