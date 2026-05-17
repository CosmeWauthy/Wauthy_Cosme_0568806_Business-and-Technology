# Preliminary Stationarity Diagnostics

- Analysis sample: `2010-08-01` to `2025-12-01`
- Monthly observations: `185`
- Duplicate months: `0`
- Missing months inside analysis span: `0`

## Integration Summary

| variable                     | label                        |   level_adf_rejects_5pct |   level_kpss_rejects_5pct |   diff_adf_rejects_5pct |   diff_kpss_rejects_5pct | plausibly_i1   | conclusion                         |
|:-----------------------------|:-----------------------------|-------------------------:|--------------------------:|------------------------:|-------------------------:|:---------------|:-----------------------------------|
| log_bitcoin_market_price_usd | Log Bitcoin market price     |                        1 |                         2 |                       2 |                        1 | False          | Ambiguous, inspect before Johansen |
| log_mci_weighted             | Log MCI, weighted efficiency |                        0 |                         2 |                       2 |                        2 | False          | Ambiguous, inspect before Johansen |
| log_mci_frontier             | Log MCI, frontier efficiency |                        0 |                         2 |                       2 |                        0 | True           | Plausibly I(1)                     |

## Descriptive Summary

| variable                     | label                        | transformation   |   n |    mean |    std |     min |     p25 |   median |     p75 |     max |
|:-----------------------------|:-----------------------------|:-----------------|----:|--------:|-------:|--------:|--------:|---------:|--------:|--------:|
| log_bitcoin_market_price_usd | Log Bitcoin market price     | level            | 185 |  7.3855 | 3.5061 | -2.7839 |  5.5793 |   8.5996 | 10.2471 | 11.6567 |
| log_mci_weighted             | Log MCI, weighted efficiency | level            | 185 | 26.0061 | 3.6344 | 13.2018 | 25.8668 |  27.4922 | 28.2486 | 29.8275 |
| log_mci_frontier             | Log MCI, frontier efficiency | level            | 185 | 23.2973 | 4.3933 | 12.0163 | 21.7132 |  25.1549 | 26.8509 | 28.4658 |
| log_bitcoin_market_price_usd | Log Bitcoin market price     | first_difference | 184 |  0.0769 | 0.2793 | -0.5340 | -0.0688 |   0.0207 |  0.1655 |  1.6411 |
| log_mci_weighted             | Log MCI, weighted efficiency | first_difference | 184 |  0.0863 | 0.3670 | -2.6973 | -0.0041 |   0.0583 |  0.1476 |  1.3667 |
| log_mci_frontier             | Log MCI, frontier efficiency | first_difference | 184 |  0.0828 | 0.3430 | -2.1012 |  0.0066 |   0.0748 |  0.1686 |  1.1265 |

## ADF and KPSS Results

| variable                     | label                        | transformation   | test   | deterministic   |   statistic |   p_value |   lags_used |   nobs |   critical_1pct |   critical_5pct |   critical_10pct | reject_at_5pct   |
|:-----------------------------|:-----------------------------|:-----------------|:-------|:----------------|------------:|----------:|------------:|-------:|----------------:|----------------:|-----------------:|:-----------------|
| log_bitcoin_market_price_usd | Log Bitcoin market price     | level            | ADF    | c               |     -2.2643 |    0.1837 |           7 |    177 |         -3.4678 |         -2.8780 |          -2.5756 | False            |
| log_bitcoin_market_price_usd | Log Bitcoin market price     | level            | ADF    | ct              |     -3.4535 |    0.0446 |           7 |    177 |         -4.0108 |         -3.4356 |          -3.1418 | True             |
| log_bitcoin_market_price_usd | Log Bitcoin market price     | level            | KPSS   | c               |      1.7891 |    0.0100 |           9 |    185 |          0.7390 |          0.4630 |           0.3470 | True             |
| log_bitcoin_market_price_usd | Log Bitcoin market price     | level            | KPSS   | ct              |      0.3617 |    0.0100 |           8 |    185 |          0.2160 |          0.1460 |           0.1190 | True             |
| log_bitcoin_market_price_usd | Log Bitcoin market price     | first_difference | ADF    | c               |     -3.7090 |    0.0040 |           6 |    177 |         -3.4678 |         -2.8780 |          -2.5756 | True             |
| log_bitcoin_market_price_usd | Log Bitcoin market price     | first_difference | ADF    | ct              |     -3.8903 |    0.0125 |           6 |    177 |         -4.0108 |         -3.4356 |          -3.1418 | True             |
| log_bitcoin_market_price_usd | Log Bitcoin market price     | first_difference | KPSS   | c               |      0.4708 |    0.0483 |           4 |    184 |          0.7390 |          0.4630 |           0.3470 | True             |
| log_bitcoin_market_price_usd | Log Bitcoin market price     | first_difference | KPSS   | ct              |      0.0708 |    0.1000 |           3 |    184 |          0.2160 |          0.1460 |           0.1190 | False            |
| log_mci_weighted             | Log MCI, weighted efficiency | level            | ADF    | c               |     -1.5783 |    0.4945 |          10 |    174 |         -3.4685 |         -2.8783 |          -2.5757 | False            |
| log_mci_weighted             | Log MCI, weighted efficiency | level            | ADF    | ct              |     -1.7085 |    0.7471 |          10 |    174 |         -4.0118 |         -3.4360 |          -3.1420 | False            |
| log_mci_weighted             | Log MCI, weighted efficiency | level            | KPSS   | c               |      1.0551 |    0.0100 |           9 |    185 |          0.7390 |          0.4630 |           0.3470 | True             |
| log_mci_weighted             | Log MCI, weighted efficiency | level            | KPSS   | ct              |      0.2891 |    0.0100 |           9 |    185 |          0.2160 |          0.1460 |           0.1190 | True             |
| log_mci_weighted             | Log MCI, weighted efficiency | first_difference | ADF    | c               |     -4.0185 |    0.0013 |           9 |    174 |         -3.4685 |         -2.8783 |          -2.5757 | True             |
| log_mci_weighted             | Log MCI, weighted efficiency | first_difference | ADF    | ct              |     -3.8021 |    0.0165 |           9 |    174 |         -4.0118 |         -3.4360 |          -3.1420 | True             |
| log_mci_weighted             | Log MCI, weighted efficiency | first_difference | KPSS   | c               |      0.6291 |    0.0200 |           6 |    184 |          0.7390 |          0.4630 |           0.3470 | True             |
| log_mci_weighted             | Log MCI, weighted efficiency | first_difference | KPSS   | ct              |      0.1937 |    0.0184 |           6 |    184 |          0.2160 |          0.1460 |           0.1190 | True             |
| log_mci_frontier             | Log MCI, frontier efficiency | level            | ADF    | c               |     -2.4251 |    0.1348 |           0 |    184 |         -3.4664 |         -2.8774 |          -2.5752 | False            |
| log_mci_frontier             | Log MCI, frontier efficiency | level            | ADF    | ct              |     -1.9779 |    0.6134 |           0 |    184 |         -4.0088 |         -3.4346 |          -3.1412 | False            |
| log_mci_frontier             | Log MCI, frontier efficiency | level            | KPSS   | c               |      1.7989 |    0.0100 |           9 |    185 |          0.7390 |          0.4630 |           0.3470 | True             |
| log_mci_frontier             | Log MCI, frontier efficiency | level            | KPSS   | ct              |      0.4127 |    0.0100 |           9 |    185 |          0.2160 |          0.1460 |           0.1190 | True             |
| log_mci_frontier             | Log MCI, frontier efficiency | first_difference | ADF    | c               |    -14.4194 |    0.0000 |           0 |    183 |         -3.4666 |         -2.8775 |          -2.5753 | True             |
| log_mci_frontier             | Log MCI, frontier efficiency | first_difference | ADF    | ct              |    -14.8465 |    0.0000 |           0 |    183 |         -4.0091 |         -3.4348 |          -3.1413 | True             |
| log_mci_frontier             | Log MCI, frontier efficiency | first_difference | KPSS   | c               |      0.4001 |    0.0771 |           1 |    184 |          0.7390 |          0.4630 |           0.3470 | False            |
| log_mci_frontier             | Log MCI, frontier efficiency | first_difference | KPSS   | ct              |      0.0345 |    0.1000 |           1 |    184 |          0.2160 |          0.1460 |           0.1190 | False            |

Notes:

- ADF null: unit root. Rejection supports stationarity under the stated deterministic specification.
- KPSS null: stationarity around the stated deterministic specification. Rejection supports nonstationarity.
- `c` means constant only; `ct` means constant plus linear trend.