# Gregory-Hansen Structural-Break Cointegration Tests

Implementation:

- R version: `R version 4.6.0 (2026-04-24)`.
- R package: `COINT` version `0.0.3`, function `GHansen()`.
- Dependent variable: `log_bitcoin_market_price_usd`.
- Cost variables: `log_mci_weighted` and `log_mci_frontier`.
- Samples: baseline `2010-08-01` to `2025-12-01`; ASIC robustness `2014-01-01` to `2025-12-01`.
- Trimming: `0.1`.
- Long-run variance setting: `use = c("nw", "ba")`.
- Note: `urca::ca.po()` is Phillips-Ouliaris, not Gregory-Hansen; it is not used as the GH test here.

Model definitions from `COINT::GHansen()`:

- `1`: C, level shift.
- `2`: C/T, level shift with trend.
- `3`: C/S, regime shift.
- `4`: regime and trend shift.

Null hypothesis: no cointegration. Rejection supports cointegration allowing one endogenous structural break.

## Strongest Test By System/Sample/Test Family

| system | sample | model | test_label | statistics | 5pct | reject_5pct | break_month |
|---|---|---|---|---|---|---|---|
| frontier | asic_robustness_2014_01 | C_T_level_shift_with_trend | ADF* | -38.7302 | -4.99 | TRUE | 2023-07-01 |
| weighted | asic_robustness_2014_01 | C_T_level_shift_with_trend | ADF* | -21.0479 | -4.99 | TRUE | 2022-04-01 |
| frontier | baseline_2010_08 | C_T_level_shift_with_trend | ADF* | -36.0594 | -4.99 | TRUE | 2021-01-01 |
| weighted | baseline_2010_08 | C_T_level_shift_with_trend | ADF* | -27.0405 | -4.99 | TRUE | 2021-12-01 |
| frontier | asic_robustness_2014_01 | C_T_level_shift_with_trend | Za* | -38.238 | -47.96 | FALSE | 2023-07-01 |
| weighted | asic_robustness_2014_01 | C_S_regime_shift | Za* | -65.3974 | -47.04 | TRUE | 2016-12-01 |
| frontier | baseline_2010_08 | C_S_regime_shift | Za* | -44.5754 | -47.04 | FALSE | 2014-02-01 |
| weighted | baseline_2010_08 | C_S_regime_shift | Za* | -46.1343 | -47.04 | FALSE | 2016-12-01 |
| frontier | asic_robustness_2014_01 | C_T_level_shift_with_trend | Zt* | -38.5013 | -4.99 | TRUE | 2023-07-01 |
| weighted | asic_robustness_2014_01 | C_T_level_shift_with_trend | Zt* | -20.9323 | -4.99 | TRUE | 2022-04-01 |
| frontier | baseline_2010_08 | C_T_level_shift_with_trend | Zt* | -35.6027 | -4.99 | TRUE | 2021-01-01 |
| weighted | baseline_2010_08 | C_T_level_shift_with_trend | Zt* | -25.0539 | -4.99 | TRUE | 2022-01-01 |

## Model Summary

| system | sample | model_id | model | any_test_rejects_5pct |
|---|---|---|---|---|
| frontier | asic_robustness_2014_01 | 1 | C_level_shift | TRUE |
| weighted | asic_robustness_2014_01 | 1 | C_level_shift | TRUE |
| frontier | baseline_2010_08 | 1 | C_level_shift | TRUE |
| weighted | baseline_2010_08 | 1 | C_level_shift | FALSE |
| frontier | asic_robustness_2014_01 | 3 | C_S_regime_shift | TRUE |
| weighted | asic_robustness_2014_01 | 3 | C_S_regime_shift | TRUE |
| frontier | baseline_2010_08 | 3 | C_S_regime_shift | TRUE |
| weighted | baseline_2010_08 | 3 | C_S_regime_shift | TRUE |
| frontier | asic_robustness_2014_01 | 2 | C_T_level_shift_with_trend | TRUE |
| weighted | asic_robustness_2014_01 | 2 | C_T_level_shift_with_trend | TRUE |
| frontier | baseline_2010_08 | 2 | C_T_level_shift_with_trend | TRUE |
| weighted | baseline_2010_08 | 2 | C_T_level_shift_with_trend | TRUE |
| frontier | asic_robustness_2014_01 | 4 | regime_and_trend_shift | FALSE |
| weighted | asic_robustness_2014_01 | 4 | regime_and_trend_shift | FALSE |
| frontier | baseline_2010_08 | 4 | regime_and_trend_shift | TRUE |
| weighted | baseline_2010_08 | 4 | regime_and_trend_shift | FALSE |

## System Summary

| system | sample | any_model_test_rejects_5pct |
|---|---|---|
| frontier | asic_robustness_2014_01 | TRUE |
| weighted | asic_robustness_2014_01 | TRUE |
| frontier | baseline_2010_08 | TRUE |
| weighted | baseline_2010_08 | TRUE |

## Full Results

| system | sample | model | test_label | statistics | 5pct | reject_5pct | break_month |
|---|---|---|---|---|---|---|---|
| weighted | baseline_2010_08 | C_level_shift | ADF* | -3.781 | -4.61 | FALSE | 2017-07-01 |
| weighted | baseline_2010_08 | C_level_shift | Zt* | -4.0849 | -4.61 | FALSE | 2017-02-01 |
| weighted | baseline_2010_08 | C_level_shift | Za* | -30.6178 | -40.48 | FALSE | 2017-02-01 |
| weighted | baseline_2010_08 | C_T_level_shift_with_trend | ADF* | -27.0405 | -4.99 | TRUE | 2021-12-01 |
| weighted | baseline_2010_08 | C_T_level_shift_with_trend | Zt* | -25.0539 | -4.99 | TRUE | 2022-01-01 |
| weighted | baseline_2010_08 | C_T_level_shift_with_trend | Za* | -29.4303 | -47.96 | FALSE | 2021-12-01 |
| weighted | baseline_2010_08 | C_S_regime_shift | ADF* | -4.1123 | -4.95 | FALSE | 2016-10-01 |
| weighted | baseline_2010_08 | C_S_regime_shift | Zt* | -5.1886 | -4.95 | TRUE | 2016-12-01 |
| weighted | baseline_2010_08 | C_S_regime_shift | Za* | -46.1343 | -47.04 | FALSE | 2016-12-01 |
| weighted | baseline_2010_08 | regime_and_trend_shift | ADF* | -5.0215 | -5.5 | FALSE | 2013-08-01 |
| weighted | baseline_2010_08 | regime_and_trend_shift | Zt* | -4.2744 | -5.5 | FALSE | 2017-02-01 |
| weighted | baseline_2010_08 | regime_and_trend_shift | Za* | -31.4522 | -58.58 | FALSE | 2017-02-01 |
| frontier | baseline_2010_08 | C_level_shift | ADF* | -5.233 | -4.61 | TRUE | 2014-06-01 |
| frontier | baseline_2010_08 | C_level_shift | Zt* | -4.7622 | -4.61 | TRUE | 2014-06-01 |
| frontier | baseline_2010_08 | C_level_shift | Za* | -34.8887 | -40.48 | FALSE | 2014-06-01 |
| frontier | baseline_2010_08 | C_T_level_shift_with_trend | ADF* | -36.0594 | -4.99 | TRUE | 2021-01-01 |
| frontier | baseline_2010_08 | C_T_level_shift_with_trend | Zt* | -35.6027 | -4.99 | TRUE | 2021-01-01 |
| frontier | baseline_2010_08 | C_T_level_shift_with_trend | Za* | -36.3015 | -47.96 | FALSE | 2020-12-01 |
| frontier | baseline_2010_08 | C_S_regime_shift | ADF* | -6.0035 | -4.95 | TRUE | 2013-11-01 |
| frontier | baseline_2010_08 | C_S_regime_shift | Zt* | -5.247 | -4.95 | TRUE | 2014-02-01 |
| frontier | baseline_2010_08 | C_S_regime_shift | Za* | -44.5754 | -47.04 | FALSE | 2014-02-01 |
| frontier | baseline_2010_08 | regime_and_trend_shift | ADF* | -6.3572 | -5.5 | TRUE | 2014-06-01 |
| frontier | baseline_2010_08 | regime_and_trend_shift | Zt* | -5.0766 | -5.5 | FALSE | 2014-02-01 |
| frontier | baseline_2010_08 | regime_and_trend_shift | Za* | -43.3773 | -58.58 | FALSE | 2014-02-01 |
| weighted | asic_robustness_2014_01 | C_level_shift | ADF* | -4.0858 | -4.61 | FALSE | 2016-10-01 |
| weighted | asic_robustness_2014_01 | C_level_shift | Zt* | -5.5768 | -4.61 | TRUE | 2017-02-01 |
| weighted | asic_robustness_2014_01 | C_level_shift | Za* | -49.0912 | -40.48 | TRUE | 2017-02-01 |
| weighted | asic_robustness_2014_01 | C_T_level_shift_with_trend | ADF* | -21.0479 | -4.99 | TRUE | 2022-04-01 |
| weighted | asic_robustness_2014_01 | C_T_level_shift_with_trend | Zt* | -20.9323 | -4.99 | TRUE | 2022-04-01 |
| weighted | asic_robustness_2014_01 | C_T_level_shift_with_trend | Za* | -21.1662 | -47.96 | FALSE | 2022-03-01 |
| weighted | asic_robustness_2014_01 | C_S_regime_shift | ADF* | -4.7872 | -4.95 | FALSE | 2018-01-01 |
| weighted | asic_robustness_2014_01 | C_S_regime_shift | Zt* | -6.3405 | -4.95 | TRUE | 2016-12-01 |
| weighted | asic_robustness_2014_01 | C_S_regime_shift | Za* | -65.3974 | -47.04 | TRUE | 2016-12-01 |
| weighted | asic_robustness_2014_01 | regime_and_trend_shift | ADF* | -4.5245 | -5.5 | FALSE | 2017-02-01 |
| weighted | asic_robustness_2014_01 | regime_and_trend_shift | Zt* | -3.969 | -5.5 | FALSE | 2017-01-01 |
| weighted | asic_robustness_2014_01 | regime_and_trend_shift | Za* | -29.0754 | -58.58 | FALSE | 2017-01-01 |
| frontier | asic_robustness_2014_01 | C_level_shift | ADF* | -4.1627 | -4.61 | FALSE | 2016-09-01 |
| frontier | asic_robustness_2014_01 | C_level_shift | Zt* | -5.2853 | -4.61 | TRUE | 2018-06-01 |
| frontier | asic_robustness_2014_01 | C_level_shift | Za* | -35.6994 | -40.48 | FALSE | 2015-02-01 |
| frontier | asic_robustness_2014_01 | C_T_level_shift_with_trend | ADF* | -38.7302 | -4.99 | TRUE | 2023-07-01 |
| frontier | asic_robustness_2014_01 | C_T_level_shift_with_trend | Zt* | -38.5013 | -4.99 | TRUE | 2023-07-01 |
| frontier | asic_robustness_2014_01 | C_T_level_shift_with_trend | Za* | -38.238 | -47.96 | FALSE | 2023-07-01 |
| frontier | asic_robustness_2014_01 | C_S_regime_shift | ADF* | -4.3259 | -4.95 | FALSE | 2016-03-01 |
| frontier | asic_robustness_2014_01 | C_S_regime_shift | Zt* | -5.2119 | -4.95 | TRUE | 2022-06-01 |
| frontier | asic_robustness_2014_01 | C_S_regime_shift | Za* | -34.325 | -47.04 | FALSE | 2022-07-01 |
| frontier | asic_robustness_2014_01 | regime_and_trend_shift | ADF* | -4.3342 | -5.5 | FALSE | 2016-03-01 |
| frontier | asic_robustness_2014_01 | regime_and_trend_shift | Zt* | -5.3154 | -5.5 | FALSE | 2020-11-01 |
| frontier | asic_robustness_2014_01 | regime_and_trend_shift | Za* | -37.2566 | -58.58 | FALSE | 2020-11-01 |
