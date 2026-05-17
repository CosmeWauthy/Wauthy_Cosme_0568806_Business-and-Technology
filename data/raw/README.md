# Raw Data

Raw data files are not included in this public repository because redistribution permissions have not yet been fully verified for all sources. The complete raw-data archive is retained by the author and can be made available to the jury upon request, subject to source-specific redistribution restrictions. Requests can be sent to [cosme.brieuc.i.wauthy@vub.be](mailto:cosme.brieuc.i.wauthy@vub.be).

To rebuild the full data pipeline from raw inputs, obtain the files below from the original sources and place them in this folder using the listed filenames.

| Expected filename | Source | Used for | Notes |
|---|---|---|---|
| `bitcoinity_data_price.csv` | Bitcoinity | Bitcoin market price in USD | Daily price export; monthly average is used in the analysis. |
| `coinmetrics_btc_community.csv` | Coin Metrics Community BTC | Blocks mined, transaction fees, issuance, and support price field | Main source for `BlkCnt`, `FeeTotNtv`, and `IssTotNtv`; miner compensation is derived from issuance plus fees. |
| `difficulty_blockchain_api_sampled-false.json` | Blockchain.com chart API, `sampled=false` | Bitcoin network difficulty | Daily difficulty series; monthly average is used in the marginal-cost index. |
| `transaction-fees_blockchain_api_sampled-false.json` | Blockchain.com chart API, `sampled=false` | Transaction-fee cross-check only | Not used in the final backbone because Coin Metrics is the main fee source. |
| `BitcoinVisuals.com_chart.csv` | BitcoinVisuals | Subsidy-regime validation | Validation only; Coin Metrics issuance is used in the final monthly panel. |
| `Mining equipment list - list.csv` | CCAF/CBECI mining equipment list | Hardware efficiency paths | Master hardware source used to construct frontier and weighted-average efficiency paths. |

All processed thesis outputs are truncated to the hard sample cutoff of `2025-12-31`.
