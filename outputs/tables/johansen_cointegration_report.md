# Johansen Cointegration Tests

Main specification:

- VAR lag order selected by AIC on levels with intercept and maximum `12` monthly lags.
- Johansen test uses a constant deterministic term (`det_order = 0`).
- `k_ar_diff = selected VAR lag order - 1`.
- No-deterministic and linear-trend specifications are retained as deterministic-term sensitivity checks.

## Main Rank Summary

| system | sample | sample_start | nobs_levels | var_lag_order_levels | k_ar_diff | trace_rank_95pct | maxeig_rank_95pct | chosen_rank_95pct | cointegration_supported_rank1 | rank_note |
|---|---|---|---|---|---|---|---|---|---|---|
| weighted | baseline_2010_08 | 2010-08-01 | 185 | 11 | 10 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| frontier | baseline_2010_08 | 2010-08-01 | 185 | 2 | 1 | 2 | 2 | 2 | False | Trace and max-eigenvalue agree on rank 2. |
| weighted | asic_robustness_2014_01 | 2014-01-01 | 144 | 2 | 1 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| frontier | asic_robustness_2014_01 | 2014-01-01 | 144 | 2 | 1 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |

## Main Cointegrating Vectors

| system | sample | det_order | deterministic | var_lag_order_levels | k_ar_diff | eigenvector_index | normalized_on | log_bitcoin_market_price_usd | log_mci_weighted | cointegration_relation | log_mci_frontier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| weighted | baseline_2010_08 | 0 | constant | 11 | 10 | 1 | log_bitcoin_market_price_usd | 1.000000 | -0.087851 | log_bitcoin_market_price_usd + (-0.087851)*log_mci_weighted |  |
| frontier | baseline_2010_08 | 0 | constant | 2 | 1 | 1 | log_bitcoin_market_price_usd | 1.000000 |  | log_bitcoin_market_price_usd + (-0.670027)*log_mci_frontier | -0.670027 |
| weighted | asic_robustness_2014_01 | 0 | constant | 2 | 1 | 1 | log_bitcoin_market_price_usd | 1.000000 | -32.112053 | log_bitcoin_market_price_usd + (-32.112053)*log_mci_weighted |  |
| frontier | asic_robustness_2014_01 | 0 | constant | 2 | 1 | 1 | log_bitcoin_market_price_usd | 1.000000 |  | log_bitcoin_market_price_usd + (-0.933361)*log_mci_frontier | -0.933361 |

## Main Test Statistics

| system | sample | test | null_rank | statistic | critical_95pct | reject_95pct |
|---|---|---|---|---|---|---|
| weighted | baseline_2010_08 | trace | 0 | 13.5821 | 15.4943 | False |
| weighted | baseline_2010_08 | max_eigenvalue | 0 | 9.6178 | 14.2639 | False |
| weighted | baseline_2010_08 | trace | 1 | 3.9644 | 3.8415 | True |
| weighted | baseline_2010_08 | max_eigenvalue | 1 | 3.9644 | 3.8415 | True |
| frontier | baseline_2010_08 | trace | 0 | 35.5536 | 15.4943 | True |
| frontier | baseline_2010_08 | max_eigenvalue | 0 | 22.2122 | 14.2639 | True |
| frontier | baseline_2010_08 | trace | 1 | 13.3414 | 3.8415 | True |
| frontier | baseline_2010_08 | max_eigenvalue | 1 | 13.3414 | 3.8415 | True |
| weighted | asic_robustness_2014_01 | trace | 0 | 5.7045 | 15.4943 | False |
| weighted | asic_robustness_2014_01 | max_eigenvalue | 0 | 4.1798 | 14.2639 | False |
| weighted | asic_robustness_2014_01 | trace | 1 | 1.5247 | 3.8415 | False |
| weighted | asic_robustness_2014_01 | max_eigenvalue | 1 | 1.5247 | 3.8415 | False |
| frontier | asic_robustness_2014_01 | trace | 0 | 30.7698 | 15.4943 | True |
| frontier | asic_robustness_2014_01 | max_eigenvalue | 0 | 29.3616 | 14.2639 | True |
| frontier | asic_robustness_2014_01 | trace | 1 | 1.4082 | 3.8415 | False |
| frontier | asic_robustness_2014_01 | max_eigenvalue | 1 | 1.4082 | 3.8415 | False |

## Lag Selection

| system | sample | criterion | selected_var_lag_order | max_var_lags | trend_used_for_var_selection |
|---|---|---|---|---|---|
| weighted | baseline_2010_08 | AIC | 11 | 12 | c |
| weighted | baseline_2010_08 | BIC | 2 | 12 | c |
| weighted | baseline_2010_08 | HQIC | 2 | 12 | c |
| weighted | baseline_2010_08 | FPE | 11 | 12 | c |
| frontier | baseline_2010_08 | AIC | 2 | 12 | c |
| frontier | baseline_2010_08 | BIC | 2 | 12 | c |
| frontier | baseline_2010_08 | HQIC | 2 | 12 | c |
| frontier | baseline_2010_08 | FPE | 2 | 12 | c |
| weighted | asic_robustness_2014_01 | AIC | 2 | 12 | c |
| weighted | asic_robustness_2014_01 | BIC | 2 | 12 | c |
| weighted | asic_robustness_2014_01 | HQIC | 2 | 12 | c |
| weighted | asic_robustness_2014_01 | FPE | 2 | 12 | c |
| frontier | asic_robustness_2014_01 | AIC | 2 | 12 | c |
| frontier | asic_robustness_2014_01 | BIC | 2 | 12 | c |
| frontier | asic_robustness_2014_01 | HQIC | 2 | 12 | c |
| frontier | asic_robustness_2014_01 | FPE | 2 | 12 | c |

## Deterministic-Term Sensitivity Summary

| system | sample | deterministic | var_lag_order_levels | trace_rank_95pct | maxeig_rank_95pct | chosen_rank_95pct | cointegration_supported_rank1 | rank_note |
|---|---|---|---|---|---|---|---|---|
| weighted | baseline_2010_08 | none | 11 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| weighted | baseline_2010_08 | constant | 11 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | baseline_2010_08 | linear_trend | 11 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| frontier | baseline_2010_08 | none | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | baseline_2010_08 | constant | 2 | 2 | 2 | 2 | False | Trace and max-eigenvalue agree on rank 2. |
| frontier | baseline_2010_08 | linear_trend | 2 | 2 | 2 | 2 | False | Trace and max-eigenvalue agree on rank 2. |
| weighted | asic_robustness_2014_01 | none | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | asic_robustness_2014_01 | constant | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | asic_robustness_2014_01 | linear_trend | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | asic_robustness_2014_01 | none | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| frontier | asic_robustness_2014_01 | constant | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | asic_robustness_2014_01 | linear_trend | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |

## Lag-Criterion Sensitivity Summary

| system | sample | criterion | deterministic | var_lag_order_levels | trace_rank_95pct | maxeig_rank_95pct | chosen_rank_95pct | cointegration_supported_rank1 | rank_note |
|---|---|---|---|---|---|---|---|---|---|
| weighted | baseline_2010_08 | AIC | none | 11 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| weighted | baseline_2010_08 | AIC | constant | 11 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | baseline_2010_08 | AIC | linear_trend | 11 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | baseline_2010_08 | BIC | none | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| weighted | baseline_2010_08 | BIC | constant | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| weighted | baseline_2010_08 | BIC | linear_trend | 2 | 2 | 0 | 0 | False | Trace rank 2 and max-eigenvalue rank 0 differ; conservative chosen rank 0. |
| weighted | baseline_2010_08 | HQIC | none | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| weighted | baseline_2010_08 | HQIC | constant | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| weighted | baseline_2010_08 | HQIC | linear_trend | 2 | 2 | 0 | 0 | False | Trace rank 2 and max-eigenvalue rank 0 differ; conservative chosen rank 0. |
| weighted | baseline_2010_08 | FPE | none | 11 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| weighted | baseline_2010_08 | FPE | constant | 11 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | baseline_2010_08 | FPE | linear_trend | 11 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| frontier | baseline_2010_08 | AIC | none | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | baseline_2010_08 | AIC | constant | 2 | 2 | 2 | 2 | False | Trace and max-eigenvalue agree on rank 2. |
| frontier | baseline_2010_08 | AIC | linear_trend | 2 | 2 | 2 | 2 | False | Trace and max-eigenvalue agree on rank 2. |
| frontier | baseline_2010_08 | BIC | none | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | baseline_2010_08 | BIC | constant | 2 | 2 | 2 | 2 | False | Trace and max-eigenvalue agree on rank 2. |
| frontier | baseline_2010_08 | BIC | linear_trend | 2 | 2 | 2 | 2 | False | Trace and max-eigenvalue agree on rank 2. |
| frontier | baseline_2010_08 | HQIC | none | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | baseline_2010_08 | HQIC | constant | 2 | 2 | 2 | 2 | False | Trace and max-eigenvalue agree on rank 2. |
| frontier | baseline_2010_08 | HQIC | linear_trend | 2 | 2 | 2 | 2 | False | Trace and max-eigenvalue agree on rank 2. |
| frontier | baseline_2010_08 | FPE | none | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | baseline_2010_08 | FPE | constant | 2 | 2 | 2 | 2 | False | Trace and max-eigenvalue agree on rank 2. |
| frontier | baseline_2010_08 | FPE | linear_trend | 2 | 2 | 2 | 2 | False | Trace and max-eigenvalue agree on rank 2. |
| weighted | asic_robustness_2014_01 | AIC | none | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | asic_robustness_2014_01 | AIC | constant | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | asic_robustness_2014_01 | AIC | linear_trend | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| weighted | asic_robustness_2014_01 | BIC | none | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | asic_robustness_2014_01 | BIC | constant | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | asic_robustness_2014_01 | BIC | linear_trend | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| weighted | asic_robustness_2014_01 | HQIC | none | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | asic_robustness_2014_01 | HQIC | constant | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | asic_robustness_2014_01 | HQIC | linear_trend | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| weighted | asic_robustness_2014_01 | FPE | none | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | asic_robustness_2014_01 | FPE | constant | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| weighted | asic_robustness_2014_01 | FPE | linear_trend | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | asic_robustness_2014_01 | AIC | none | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| frontier | asic_robustness_2014_01 | AIC | constant | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | asic_robustness_2014_01 | AIC | linear_trend | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | asic_robustness_2014_01 | BIC | none | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| frontier | asic_robustness_2014_01 | BIC | constant | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | asic_robustness_2014_01 | BIC | linear_trend | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | asic_robustness_2014_01 | HQIC | none | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| frontier | asic_robustness_2014_01 | HQIC | constant | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | asic_robustness_2014_01 | HQIC | linear_trend | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | asic_robustness_2014_01 | FPE | none | 2 | 0 | 0 | 0 | False | Trace and max-eigenvalue both fail to support cointegration. |
| frontier | asic_robustness_2014_01 | FPE | constant | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |
| frontier | asic_robustness_2014_01 | FPE | linear_trend | 2 | 1 | 1 | 1 | True | Trace and max-eigenvalue both support one cointegrating relation. |

Interpretation note:

- A rank of `1` in a bivariate system supports one cointegrating relation.
- A rank of `0` does not support cointegration under that specification.
- A rank of `2` would imply both variables are stationary in levels and should be treated cautiously given the prior integration-order decision.