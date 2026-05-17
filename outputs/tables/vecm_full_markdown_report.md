# VECM Estimation and Adjustment-Coefficient Report

## Purpose

This report summarizes the rank-1 VECM estimations used to interpret how Bitcoin price and the marginal-cost index adjust toward a long-run equilibrium. The estimations follow the documented Johansen and Gregory-Hansen cointegration evidence and are limited to rank-1 candidate systems.

## Basic Interpretation

The strongest and most thesis-ready specification is the frontier ASIC-era VECM with a restricted constant. This model uses the frontier marginal-cost index from `2014-01` to `2025-12`, has one cointegrating relation, and passes the 12-lag residual-whiteness diagnostic. Its adjustment coefficients suggest that the constructed frontier MCI responds clearly to disequilibrium, while Bitcoin price adjustment is weaker and only marginally significant at the 10 percent level.

The weighted-MCI results should be interpreted as secondary sensitivity evidence. The weighted full-sample parsimonious specification produces statistically significant adjustment coefficients, but the coefficients are very small, the cointegrating vector is economically awkward, and residual autocorrelation remains. The weighted ASIC-era trend specification gives only marginal evidence of price adjustment and no conventional evidence of weighted-MCI adjustment.

Overall, the VECM stage supports a cautious interpretation: the frontier marginal-cost measure provides the clearest evidence of a long-run price-cost relation, but the adjustment mechanism is not stable across specifications. This reinforces the need for rolling-window VECM analysis.

## Key Result

- Primary specification: `frontier_asic_constant_main`.
- Price adjustment coefficient: `-0.0457`, p-value `0.0664`, marginal at 10 percent.
- Frontier MCI adjustment coefficient: `0.1563`, p-value `< 0.001`, significant at 5 percent.
- Residual whiteness: fail to reject autocorrelation at 12 lags, p-value `0.7962`.
- Residual normality: rejected, so inference should remain cautious.

## Full Table 1: Estimated Specifications

| specification | system | sample | sample_start | sample_end | nobs_levels | nobs_vecm | variables | var_lag_order_levels | k_ar_diff | coint_rank | deterministic | deterministic_label | role | rationale | log_likelihood |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | 2014-01-01 | 2025-12-01 | 144 | 142 | log_bitcoin_market_price_usd, log_mci_frontier | 2 | 1 | 1 | ci | restricted_constant | primary frontier ASIC-era VECM | Johansen trace and max-eigenvalue tests support rank 1 under the constant specification across lag criteria in the ASIC-period sample. | 115.032110 |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | 2010-08-01 | 2025-12-01 | 185 | 183 | log_bitcoin_market_price_usd, log_mci_weighted | 2 | 1 | 1 | ci | restricted_constant | secondary weighted full-sample VECM | BIC and HQIC select 2 VAR lags and support rank 1 under the constant specification; AIC/FPE over-parameterised 11-lag results are treated as sensitivity evidence. | -55.183771 |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | 2010-08-01 | 2025-12-01 | 185 | 183 | log_bitcoin_market_price_usd, log_mci_frontier | 2 | 1 | 1 | n | none | frontier full-sample deterministic-term sensitivity | Full-sample frontier Johansen tests support rank 1 only without deterministic terms; constant and trend specifications return rank 2 and are not used for rank-1 VECM interpretation. | -53.075866 |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | 2014-01-01 | 2025-12-01 | 144 | 142 | log_bitcoin_market_price_usd, log_mci_weighted | 2 | 1 | 1 | li | restricted_linear_trend | weighted ASIC-era deterministic-term sensitivity | Weighted ASIC-period Johansen tests support rank 1 only with a linear-trend deterministic specification, so this is retained as a weaker sensitivity case. | 18.584004 |

## Full Table 2: Cointegrating Relations

| specification | system | sample | variable | label | beta | std_err | z_stat | p_value |
|---|---|---|---|---|---|---|---|---|
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | log_bitcoin_market_price_usd | Log Bitcoin market price | 1.000000 | 0.000000 | 0.000000 | 0.000000 |
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | log_mci_frontier | Log MCI, frontier efficiency | -0.942913 | 0.039609 | -23.805387 | 0.000000 |
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | restricted_constant | restricted_constant | 15.291692 | 1.011470 | 15.118291 | 0.000000 |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | log_bitcoin_market_price_usd | Log Bitcoin market price | 1.000000 | 0.000000 | 0.000000 | 0.000000 |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | log_mci_weighted | Log MCI, weighted efficiency | 16.264717 | 3.672647 | 4.428609 | 0.000009 |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | restricted_constant | restricted_constant | -470.311010 | 98.036531 | -4.797304 | 0.000002 |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | log_bitcoin_market_price_usd | Log Bitcoin market price | 1.000000 | 0.000000 | 0.000000 | 0.000000 |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | log_mci_frontier | Log MCI, frontier efficiency | -0.394459 | 0.017759 | -22.211794 | 0.000000 |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | log_bitcoin_market_price_usd | Log Bitcoin market price | 1.000000 | 0.000000 | 0.000000 | 0.000000 |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | log_mci_weighted | Log MCI, weighted efficiency | -0.223019 | 0.026198 | -8.512705 | 0.000000 |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | restricted_linear_trend | restricted_linear_trend | -0.042059 | 0.008718 | -4.824184 | 0.000001 |

## Full Table 3: Adjustment Coefficients

| specification | system | sample | equation | variable | label | alpha | std_err | z_stat | p_value | significant_5pct | significant_10pct | adjustment_interpretation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | delta_log_bitcoin_market_price_usd | log_bitcoin_market_price_usd | Log Bitcoin market price | -0.045675 | 0.024878 | -1.835977 | 0.066361 | False | True | Bitcoin price falls when the lagged equilibrium error is positive; marginally significant at 10%. |
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | delta_log_mci_frontier | log_mci_frontier | Log MCI, frontier efficiency | 0.156260 | 0.026222 | 5.959124 | 0.000000 | True | True | Frontier MCI rises when the lagged equilibrium error is positive; statistically significant at 5%. |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | delta_log_bitcoin_market_price_usd | log_bitcoin_market_price_usd | Log Bitcoin market price | -0.001157 | 0.000284 | -4.078806 | 0.000045 | True | True | Bitcoin price falls when the lagged equilibrium error is positive; statistically significant at 5%. |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | delta_log_mci_weighted | log_mci_weighted | Log MCI, weighted efficiency | -0.001415 | 0.000378 | -3.747247 | 0.000179 | True | True | Weighted MCI falls when the lagged equilibrium error is positive; statistically significant at 5%. |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | delta_log_bitcoin_market_price_usd | log_bitcoin_market_price_usd | Log Bitcoin market price | -0.031548 | 0.007631 | -4.133964 | 0.000036 | True | True | Bitcoin price falls when the lagged equilibrium error is positive; statistically significant at 5%. |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | delta_log_mci_frontier | log_mci_frontier | Log MCI, frontier efficiency | -0.037177 | 0.010321 | -3.602066 | 0.000316 | True | True | Frontier MCI falls when the lagged equilibrium error is positive; statistically significant at 5%. |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | delta_log_bitcoin_market_price_usd | log_bitcoin_market_price_usd | Log Bitcoin market price | -0.028952 | 0.015042 | -1.924749 | 0.054261 | False | True | Bitcoin price falls when the lagged equilibrium error is positive; marginally significant at 10%. |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | delta_log_mci_weighted | log_mci_weighted | Log MCI, weighted efficiency | 0.050409 | 0.031346 | 1.608147 | 0.107803 | False | False | Weighted MCI rises when the lagged equilibrium error is positive; not statistically significant at conventional levels. |

## Full Table 4: Short-Run Coefficients

| specification | system | sample | equation | lag | lagged_difference | coefficient | std_err | z_stat | p_value | significant_5pct |
|---|---|---|---|---|---|---|---|---|---|---|
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | delta_log_bitcoin_market_price_usd | 1 | delta_log_bitcoin_market_price_usd | 0.459666 | 0.078124 | 5.883819 | 0.000000 | True |
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | delta_log_bitcoin_market_price_usd | 1 | delta_log_mci_frontier | 0.092103 | 0.070094 | 1.313996 | 0.188848 | False |
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | delta_log_mci_frontier | 1 | delta_log_bitcoin_market_price_usd | 0.070707 | 0.082346 | 0.858660 | 0.390528 | False |
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | delta_log_mci_frontier | 1 | delta_log_mci_frontier | 0.020142 | 0.073882 | 0.272622 | 0.785143 | False |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | delta_log_bitcoin_market_price_usd | 1 | delta_log_bitcoin_market_price_usd | 0.364636 | 0.069194 | 5.269743 | 0.000000 | True |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | delta_log_bitcoin_market_price_usd | 1 | delta_log_mci_weighted | -0.012275 | 0.052381 | -0.234346 | 0.814717 | False |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | delta_log_mci_weighted | 1 | delta_log_bitcoin_market_price_usd | 0.308205 | 0.092116 | 3.345856 | 0.000820 | True |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | delta_log_mci_weighted | 1 | delta_log_mci_weighted | 0.135279 | 0.069732 | 1.939973 | 0.052383 | False |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | delta_log_bitcoin_market_price_usd | 1 | delta_log_bitcoin_market_price_usd | 0.384400 | 0.064501 | 5.959639 | 0.000000 | True |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | delta_log_bitcoin_market_price_usd | 1 | delta_log_mci_frontier | 0.060595 | 0.052497 | 1.154273 | 0.248388 | False |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | delta_log_mci_frontier | 1 | delta_log_bitcoin_market_price_usd | 0.085931 | 0.087232 | 0.985091 | 0.324579 | False |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | delta_log_mci_frontier | 1 | delta_log_mci_frontier | -0.043968 | 0.070997 | -0.619285 | 0.535729 | False |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | delta_log_bitcoin_market_price_usd | 1 | delta_log_bitcoin_market_price_usd | 0.423799 | 0.074873 | 5.660257 | 0.000000 | True |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | delta_log_bitcoin_market_price_usd | 1 | delta_log_mci_weighted | -0.032475 | 0.039586 | -0.820362 | 0.412010 | False |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | delta_log_mci_weighted | 1 | delta_log_bitcoin_market_price_usd | 0.094275 | 0.156031 | 0.604206 | 0.545707 | False |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | delta_log_mci_weighted | 1 | delta_log_mci_weighted | -0.025250 | 0.082496 | -0.306070 | 0.759551 | False |

## Full Table 5: Residual Diagnostics

| specification | system | sample | whiteness_nlags | whiteness_statistic | whiteness_p_value | whiteness_conclusion | normality_statistic | normality_p_value | normality_conclusion |
|---|---|---|---|---|---|---|---|---|---|
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | 12 | 34.265355 | 0.796198 | fail to reject | 876.778012 | 0.000000 | reject |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | 12 | 87.662666 | 0.000046 | reject | 12093.761387 | 0.000000 | reject |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | 12 | 103.243185 | 0.000000 | reject | 2972.770076 | 0.000000 | reject |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | 12 | 61.981743 | 0.024005 | reject | 11311.237700 | 0.000000 | reject |

## Thesis-Ready Takeaway

The rank-1 VECM results indicate that the frontier marginal-cost index is the most credible cost measure for adjustment-coefficient interpretation. In the cleanest ASIC-era specification, the frontier MCI adjusts strongly to the lagged equilibrium error, while Bitcoin price adjustment is weaker and only marginally significant. Weighted-MCI specifications remain useful as robustness checks, but their adjustment results are more fragile and diagnostically weaker.