# Monthly Master Panel Audit

Sources:

- `data/processed/backbone/backbone_monthly.csv`
- `data/processed/hardware/frontier_efficiency_monthly.csv`
- `data/processed/hardware/weighted_efficiency_monthly.csv`

Formula implementation:

- `miner_compensation_per_block_btc_monthly = total_miner_compensation_btc_monthly / blocks_mined_monthly`
- `energy_per_block_j = eta_j_per_th * network_difficulty_monthly * 2^32 / 10^12`
- `mci_j_per_btc = energy_per_block_j / miner_compensation_per_block_btc_monthly`

- `HASHES_PER_DIFFICULTY`: 4294967296
- `HASHES_PER_TH`: 1000000000000

- `rows`: 204
- `min_month`: 2009-01-01
- `max_month`: 2025-12-01
- `missing_months_inside_span`: 0
- `analysis_rows`: 185
- `analysis_min_month`: 2010-08-01
- `analysis_max_month`: 2025-12-01
- `analysis_missing_bitcoin_market_price_usd_monthly`: 0
- `analysis_nonpositive_bitcoin_market_price_usd_monthly`: 0
- `analysis_missing_network_difficulty_monthly`: 0
- `analysis_nonpositive_network_difficulty_monthly`: 0
- `analysis_missing_miner_compensation_per_block_btc_monthly`: 0
- `analysis_nonpositive_miner_compensation_per_block_btc_monthly`: 0
- `analysis_missing_frontier_efficiency_j_per_th`: 0
- `analysis_nonpositive_frontier_efficiency_j_per_th`: 0
- `analysis_missing_eta_weighted_avg_j_per_th`: 0
- `analysis_nonpositive_eta_weighted_avg_j_per_th`: 0
- `analysis_missing_mci_frontier_j_per_btc`: 0
- `analysis_nonpositive_mci_frontier_j_per_btc`: 0
- `analysis_missing_mci_weighted_j_per_btc`: 0
- `analysis_nonpositive_mci_weighted_j_per_btc`: 0
- `analysis_missing_log_bitcoin_market_price_usd`: 0
- `analysis_nonfinite_log_bitcoin_market_price_usd`: 0
- `analysis_missing_log_mci_frontier`: 0
- `analysis_nonfinite_log_mci_frontier`: 0
- `analysis_missing_log_mci_weighted`: 0
- `analysis_nonfinite_log_mci_weighted`: 0