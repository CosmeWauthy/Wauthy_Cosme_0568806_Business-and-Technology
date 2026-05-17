# Supplementary Stationarity Checks

- Baseline sample: `2010-08-01` to `2025-12-01`
- Checks: KPSS lag/bandwidth sensitivity, Zivot-Andrews break-aware unit-root tests, and later-start sample sensitivity.

## Overall Summary

| variable | label | za_level_rejections_5pct | za_level_specs_checked | baseline_later_start_i1_support | supplementary_interpretation |
|---|---|---|---|---|---|
| log_bitcoin_market_price_usd | Log Bitcoin market price | 3 | 3 | False | I(1) support appears in 4 of 5 sample-start checks; interpret alongside break-aware evidence. |
| log_mci_weighted | Log MCI, weighted efficiency | 2 | 3 | False | ADF supports stationary first differences and KPSS rejection is bandwidth-fragile; I(1) interpretation is strengthened with lifecycle-rule caveat. |
| log_mci_frontier | Log MCI, frontier efficiency | 2 | 3 | True | Supplementary evidence remains consistent with the preliminary I(1) interpretation. |

## Weighted-MCI KPSS Bandwidth Sensitivity

| variable | transformation | deterministic | kpss_rejections_at_5pct | kpss_specs_checked | min_statistic | max_statistic | min_lags_used | max_lags_used | fragility_conclusion |
|---|---|---|---|---|---|---|---|---|---|
| log_mci_weighted | first_difference | c | 9 | 12 | 0.3925 | 1.1138 | 1 | 24 | Fragile to bandwidth |
| log_mci_weighted | first_difference | ct | 10 | 12 | 0.1422 | 0.3133 | 1 | 24 | Fragile to bandwidth |

Interpretation: the weighted-MCI first-difference KPSS result is evaluated specifically as a possible long-run-variance/bandwidth artefact around hardware lifecycle transitions.

## Zivot-Andrews Level Tests

| variable | break_specification | statistic | p_value | break_month | reject_unit_root_at_5pct |
|---|---|---|---|---|---|
| log_bitcoin_market_price_usd | c | -5.3467 | 0.0075 | 2013-01-01 | True |
| log_bitcoin_market_price_usd | t | -4.7559 | 0.0210 | 2017-11-01 | True |
| log_bitcoin_market_price_usd | ct | -5.2234 | 0.0332 | 2013-01-01 | True |
| log_mci_weighted | c | -4.2381 | 0.2199 | 2013-04-01 | False |
| log_mci_weighted | t | -5.2879 | 0.0058 | 2013-12-01 | True |
| log_mci_weighted | ct | -5.7159 | 0.0062 | 2016-03-01 | True |
| log_mci_frontier | c | -5.1261 | 0.0193 | 2013-05-01 | True |
| log_mci_frontier | t | -3.2768 | 0.4855 | 2014-06-01 | False |
| log_mci_frontier | ct | -5.0734 | 0.0500 | 2013-06-01 | True |

## Later-Start Summary for Weighted MCI

| sample_start | sample_end | nobs_levels | variable | label | level_adf_rejects_5pct | level_kpss_rejects_5pct | diff_adf_rejects_5pct | diff_kpss_rejects_5pct | i1_support | note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2010-08-01 | 2025-12-01 | 185 | log_mci_weighted | Log MCI, weighted efficiency | 0 | 2 | 2 | 2 | False | Treat level ADF rejections cautiously when breaks/trends are plausible |
| 2012-01-01 | 2025-12-01 | 168 | log_mci_weighted | Log MCI, weighted efficiency | 2 | 2 | 0 | 1 | False | Treat level ADF rejections cautiously when breaks/trends are plausible |
| 2013-01-01 | 2025-12-01 | 156 | log_mci_weighted | Log MCI, weighted efficiency | 1 | 0 | 1 | 1 | False | Treat level ADF rejections cautiously when breaks/trends are plausible |
| 2014-01-01 | 2025-12-01 | 144 | log_mci_weighted | Log MCI, weighted efficiency | 0 | 1 | 2 | 0 | True | Treat level ADF rejections cautiously when breaks/trends are plausible |
| 2016-01-01 | 2025-12-01 | 120 | log_mci_weighted | Log MCI, weighted efficiency | 1 | 2 | 2 | 0 | True | Treat level ADF rejections cautiously when breaks/trends are plausible |

Notes:

- KPSS null: stationarity around the deterministic specification; rejection supports nonstationarity.
- ADF and Zivot-Andrews null: unit root; rejection supports stationarity, with Zivot-Andrews allowing one endogenous break.
- `c` means intercept, `t` means trend, and `ct` means both intercept and trend/break specification depending on the test.