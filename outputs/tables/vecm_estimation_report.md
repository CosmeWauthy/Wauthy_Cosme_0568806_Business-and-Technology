# Rank-1 VECM Estimation

Purpose: estimate only the documented rank-1 candidate systems and interpret adjustment coefficients.

Implementation:

- Python `statsmodels.tsa.vector_ar.vecm.VECM`.
- Dependent systems are bivariate: log Bitcoin price with one log MCI measure.
- `k_ar_diff = VAR lag order - 1`; all estimated specifications use `k_ar_diff = 1`.
- Constant Johansen cases are estimated as restricted constants in the cointegrating relation (`deterministic = 'ci'`).
- No-deterministic sensitivity uses `deterministic = 'n'`; linear-trend sensitivity uses a restricted trend (`deterministic = 'li'`).

## Estimated Specifications

| specification | system | sample | sample_start | sample_end | nobs_levels | var_lag_order_levels | k_ar_diff | deterministic_label | role |
|---|---|---|---|---|---|---|---|---|---|
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | 2014-01-01 | 2025-12-01 | 144 | 2 | 1 | restricted_constant | primary frontier ASIC-era VECM |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | 2010-08-01 | 2025-12-01 | 185 | 2 | 1 | restricted_constant | secondary weighted full-sample VECM |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | 2010-08-01 | 2025-12-01 | 185 | 2 | 1 | none | frontier full-sample deterministic-term sensitivity |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | 2014-01-01 | 2025-12-01 | 144 | 2 | 1 | restricted_linear_trend | weighted ASIC-era deterministic-term sensitivity |

## Adjustment Coefficients

| specification | equation | alpha | std_err | z_stat | p_value | significant_5pct | significant_10pct |
|---|---|---|---|---|---|---|---|
| frontier_asic_constant_main | delta_log_bitcoin_market_price_usd | -0.0457 | 0.0249 | -1.8360 | 0.0664 | False | True |
| frontier_asic_constant_main | delta_log_mci_frontier | 0.1563 | 0.0262 | 5.9591 | 0.0000 | True | True |
| weighted_baseline_parsimonious_constant | delta_log_bitcoin_market_price_usd | -0.0012 | 0.0003 | -4.0788 | 0.0000 | True | True |
| weighted_baseline_parsimonious_constant | delta_log_mci_weighted | -0.0014 | 0.0004 | -3.7472 | 0.0002 | True | True |
| frontier_baseline_none_sensitivity | delta_log_bitcoin_market_price_usd | -0.0315 | 0.0076 | -4.1340 | 0.0000 | True | True |
| frontier_baseline_none_sensitivity | delta_log_mci_frontier | -0.0372 | 0.0103 | -3.6021 | 0.0003 | True | True |
| weighted_asic_linear_trend_sensitivity | delta_log_bitcoin_market_price_usd | -0.0290 | 0.0150 | -1.9247 | 0.0543 | False | True |
| weighted_asic_linear_trend_sensitivity | delta_log_mci_weighted | 0.0504 | 0.0313 | 1.6081 | 0.1078 | False | False |

## Price-Adjustment Reading

| specification | system | sample | alpha | p_value | adjustment_interpretation |
|---|---|---|---|---|---|
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | -0.0457 | 0.0664 | Bitcoin price falls when the lagged equilibrium error is positive; marginally significant at 10%. |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | -0.0012 | 0.0000 | Bitcoin price falls when the lagged equilibrium error is positive; statistically significant at 5%. |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | -0.0315 | 0.0000 | Bitcoin price falls when the lagged equilibrium error is positive; statistically significant at 5%. |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | -0.0290 | 0.0543 | Bitcoin price falls when the lagged equilibrium error is positive; marginally significant at 10%. |

## Cost-Adjustment Reading

| specification | system | sample | alpha | p_value | adjustment_interpretation |
|---|---|---|---|---|---|
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | 0.1563 | 0.0000 | Frontier MCI rises when the lagged equilibrium error is positive; statistically significant at 5%. |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | -0.0014 | 0.0002 | Weighted MCI falls when the lagged equilibrium error is positive; statistically significant at 5%. |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | -0.0372 | 0.0003 | Frontier MCI falls when the lagged equilibrium error is positive; statistically significant at 5%. |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | 0.0504 | 0.1078 | Weighted MCI rises when the lagged equilibrium error is positive; not statistically significant at conventional levels. |

## Cointegrating Relations

| specification | variable | beta | std_err | z_stat | p_value |
|---|---|---|---|---|---|
| frontier_asic_constant_main | log_bitcoin_market_price_usd | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| frontier_asic_constant_main | log_mci_frontier | -0.9429 | 0.0396 | -23.8054 | 0.0000 |
| frontier_asic_constant_main | restricted_constant | 15.2917 | 1.0115 | 15.1183 | 0.0000 |
| weighted_baseline_parsimonious_constant | log_bitcoin_market_price_usd | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| weighted_baseline_parsimonious_constant | log_mci_weighted | 16.2647 | 3.6726 | 4.4286 | 0.0000 |
| weighted_baseline_parsimonious_constant | restricted_constant | -470.3110 | 98.0365 | -4.7973 | 0.0000 |
| frontier_baseline_none_sensitivity | log_bitcoin_market_price_usd | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| frontier_baseline_none_sensitivity | log_mci_frontier | -0.3945 | 0.0178 | -22.2118 | 0.0000 |
| weighted_asic_linear_trend_sensitivity | log_bitcoin_market_price_usd | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| weighted_asic_linear_trend_sensitivity | log_mci_weighted | -0.2230 | 0.0262 | -8.5127 | 0.0000 |
| weighted_asic_linear_trend_sensitivity | restricted_linear_trend | -0.0421 | 0.0087 | -4.8242 | 0.0000 |

## Residual Diagnostics

| specification | whiteness_nlags | whiteness_p_value | whiteness_conclusion | normality_p_value | normality_conclusion |
|---|---|---|---|---|---|
| frontier_asic_constant_main | 12 | 0.7962 | fail to reject | 0.0000 | reject |
| weighted_baseline_parsimonious_constant | 12 | 0.0000 | reject | 0.0000 | reject |
| frontier_baseline_none_sensitivity | 12 | 0.0000 | reject | 0.0000 | reject |
| weighted_asic_linear_trend_sensitivity | 12 | 0.0240 | reject | 0.0000 | reject |

Interpretation note:

- A negative price adjustment coefficient means Bitcoin price tends to fall after a positive lagged equilibrium error.
- A positive cost adjustment coefficient means the MCI tends to rise after that same error.
- Because the cointegrating vector is normalized on log price, the error is approximately `log_price - beta_cost * log_cost + deterministic term`.
- These VECM results remain specification-dependent and should be read alongside the Gregory-Hansen break evidence.