# Data Dictionary

## Sample

The main monthly analysis sample runs from `2010-08-01` through `2025-12-01`. Dates are stored as month-start dates.

## Final Monthly Panel

File: `data/processed/monthly/monthly_master_panel.csv`

| Variable | Unit / type | Description |
|---|---|---|
| `month` | Date | Month-start observation date. |
| `bitcoin_market_price_usd` | USD/BTC | Monthly arithmetic mean Bitcoin market price from Bitcoinity. |
| `network_difficulty` | Difficulty units | Monthly arithmetic mean Bitcoin network difficulty. |
| `blocks_mined` | Blocks | Monthly total number of blocks mined. |
| `total_transaction_fees_btc` | BTC | Monthly total transaction fees. |
| `new_coins_issued_btc` | BTC | Monthly total newly issued coins. |
| `total_miner_compensation_btc` | BTC | Monthly total issuance plus transaction-fee compensation. |
| `miner_compensation_per_block_btc` | BTC/block | Monthly total miner compensation divided by monthly blocks mined. |
| `frontier_efficiency_j_per_th` | J/TH | Monthly hardware efficiency of the best available device up to that month. |
| `eta_weighted_avg` | J/TH | Lifecycle-weighted average hardware efficiency. |
| `mci_frontier_j_per_btc` | J/BTC | Marginal-cost index using the frontier efficiency path. |
| `mci_weighted_j_per_btc` | J/BTC | Marginal-cost index using the weighted-average efficiency path. |
| `log_bitcoin_market_price_usd` | Natural log | Log of monthly Bitcoin market price. |
| `log_mci_frontier` | Natural log | Log of frontier marginal-cost index. |
| `log_mci_weighted` | Natural log | Log of weighted marginal-cost index. |
| `analysis_sample` | Boolean | Indicates the current econometric analysis sample. |

## Hardware Dataset

Intermediate file created by `scripts/analysis/02_prepare_hardware.py`: `data/processed/hardware/hardware_master_clean.csv`

This file is not included in the public repository because it is derived directly from the CCAF/CBECI raw hardware file. The final analysis dataset includes the constructed hardware-efficiency paths and marginal-cost variables used in the econometric analysis.

| Variable | Unit / type | Description |
|---|---|---|
| `hardware_model` | Text | Hardware model name from the CCAF/CBECI mining equipment list. |
| `hardware_type` | Text | CPU, GPU, FPGA, or ASIC. Missing post-2013 values are filled as ASIC. |
| `release_date` | Date | Device release date from the source file. |
| `release_timestamp_unix` | Unix timestamp | Release timestamp where available. |
| `hashrate_th_s` | TH/s | Device hashrate converted to terahashes per second. |
| `power_w` | Watts | Device power consumption. |
| `efficiency_j_per_gh` | J/GH | Source efficiency where available. |
| `efficiency_j_per_th` | J/TH | Efficiency converted to joules per terahash. |
| `hardware_type_filled_post_2013_as_asic` | Boolean | Marks rows whose type was filled using the post-2013 ASIC rule. |

## Marginal-Cost Formula

For each hardware-efficiency path, the marginal-cost index is:

```text
MCI_t = eta_t * D_t * 2^32 / (10^12 * R_t)
```

where `eta_t` is hardware efficiency in J/TH, `D_t` is monthly average network difficulty, and `R_t` is monthly average miner compensation per block in BTC.
