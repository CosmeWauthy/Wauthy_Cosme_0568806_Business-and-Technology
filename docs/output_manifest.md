# Output Manifest

This file maps repository outputs to the scripts that create them.

## Figures

| Output | Script |
|---|---|
| `outputs/figures/bitcoin_price_timeseries_events.png` | `scripts/figures/01_plot_bitcoin_price_events.R` |
| `outputs/figures/preliminary_diagnostics_levels_diffs.png` | `scripts/analysis/07_preliminary_diagnostics.py` |
| `outputs/figures/rolling_vecm_combined_frontier_weighted_r.png` | `scripts/figures/02_plot_results_rolling_vecm.R` |
| `outputs/figures/figure_B1_rolling_vecm_36m_asic.png` | `scripts/figures/03_generate_appendix_b_figures.R` |
| `outputs/figures/figure_B2_rolling_vecm_48m_fullsample.png` | `scripts/figures/03_generate_appendix_b_figures.R` |
| `outputs/figures/figure_B3_rolling_vecm_36m_fullsample.png` | `scripts/figures/03_generate_appendix_b_figures.R` |
| `outputs/figures/figure_B4_levels_first_differences.png` | `scripts/figures/03_generate_appendix_b_figures.R` |
| `outputs/figures/figure_B5_gregory_hansen_break_timeline.png` | `scripts/figures/03_generate_appendix_b_figures.R` |

## Tables and Reports

| Output family | Script |
|---|---|
| `preliminary_diagnostics_*.csv`, `preliminary_stationarity_diagnostics.md`, `stationarity_*.csv` | `scripts/analysis/07_preliminary_diagnostics.py` |
| `supplementary_*.csv`, `supplementary_stationarity_checks.md` | `scripts/analysis/08_supplementary_stationarity_checks.py` |
| `johansen_*.csv`, `johansen_cointegration_report.md` | `scripts/analysis/09_johansen_cointegration.py` |
| `gregory_hansen_*.csv`, `gregory_hansen_report.md` | `scripts/analysis/10_gregory_hansen_tests.R` |
| `vecm_*.csv`, `vecm_estimation_report.md` | `scripts/analysis/11_vecm_estimation.py` |
| `vecm_full_markdown_report.md` | `scripts/analysis/12_write_vecm_full_markdown_report.py` |
| `rolling_vecm_*.csv`, `rolling_vecm_report.md` | `scripts/analysis/13_rolling_vecm.py` |
| `weak_exogeneity_*.csv`, `weak_exogeneity_report.md` | `scripts/analysis/14_weak_exogeneity_tests.R` |

## Final Dataset

| Output | Script |
|---|---|
| `data/processed/monthly/monthly_master_panel.csv` | `scripts/analysis/06_construct_monthly_master_panel.py` |
| `data/processed/monthly/monthly_master_panel_audit.md` | `scripts/analysis/06_construct_monthly_master_panel.py` |
