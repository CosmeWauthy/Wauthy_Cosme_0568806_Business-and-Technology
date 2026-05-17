# Rolling-Window VECM Results

Purpose: examine whether the VECM adjustment mechanism is stable over time after the static Johansen, Gregory-Hansen, and VECM results indicated specification sensitivity and structural instability.

Interpretive hierarchy from previous tests:

- The frontier ASIC-era restricted-constant VECM is the main specification.
- Weighted-MCI systems are robustness evidence only because static weighted results are fragile and the weighted baseline has a same-sign alpha problem.
- Full-sample frontier results are instability evidence, not a preferred adjustment model.
- Gregory-Hansen break evidence implies that rolling-window results should be read as time-varying adjustment, not as a single stable full-sample relationship.

## Main Frontier ASIC-Era Rolling Summary

| specification | window_months | n_windows | first_window_end | last_window_end | beta_cost_median | alpha_price_median | alpha_cost_median | share_price_sig_10pct | share_cost_sig_5pct | share_opposite_sign_alphas | share_cost_side_dominant_5pct | share_both_adjust_5pct | share_neither_adjust_5pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| frontier_asic_constant_main | 48 | 97 | 2017-12-01 | 2025-12-01 | -0.9971 | -0.0515 | 0.0779 | 0.4742 | 0.6804 | 0.6495 | 0.5670 | 0.1134 | 0.0619 |
| frontier_asic_constant_main | 36 | 109 | 2016-12-01 | 2025-12-01 | -1.0516 | -0.0663 | 0.1769 | 0.4862 | 0.6881 | 0.5872 | 0.5229 | 0.1651 | 0.0642 |

## Robustness Rolling Summary

| specification | window_months | n_windows | beta_cost_median | alpha_price_median | alpha_cost_median | share_price_sig_10pct | share_cost_sig_5pct | share_opposite_sign_alphas | share_same_sign_alphas |
|---|---|---|---|---|---|---|---|---|---|
| frontier_asic_constant_main | 48 | 97 | -0.9971 | -0.0515 | 0.0779 | 0.4742 | 0.6804 | 0.6495 | 0.3505 |
| frontier_asic_constant_main | 36 | 109 | -1.0516 | -0.0663 | 0.1769 | 0.4862 | 0.6881 | 0.5872 | 0.4128 |
| weighted_baseline_parsimonious_constant | 48 | 138 | -0.2722 | -0.1028 | 0.0118 | 0.8406 | 0.4493 | 0.5507 | 0.4493 |
| weighted_baseline_parsimonious_constant | 36 | 150 | -0.2875 | -0.1191 | 0.0134 | 0.7333 | 0.5133 | 0.5067 | 0.4933 |
| frontier_baseline_none_sensitivity | 48 | 138 | -0.3687 | -0.0573 | 0.0198 | 0.5870 | 0.3188 | 0.4275 | 0.5725 |
| frontier_baseline_none_sensitivity | 36 | 150 | -0.3431 | -0.0691 | 0.0391 | 0.6800 | 0.3533 | 0.4867 | 0.5133 |
| weighted_asic_linear_trend_sensitivity | 48 | 97 | -0.3322 | -0.0773 | 0.0619 | 0.8763 | 0.4124 | 0.5876 | 0.4124 |
| weighted_asic_linear_trend_sensitivity | 36 | 109 | -0.3382 | -0.1088 | 0.1003 | 0.8624 | 0.4495 | 0.7064 | 0.2936 |

## Regime Summary By Window End

| specification | window_months | window_end_regime | n_windows | alpha_price_median | alpha_cost_median | beta_cost_median | share_price_sig_10pct | share_cost_sig_5pct | share_opposite_sign_alphas |
|---|---|---|---|---|---|---|---|---|---|
| frontier_asic_constant_main | 48 | through_2020 | 37 | -0.0374 | 0.2760 | -1.0530 | 0.0541 | 1.0000 | 0.6486 |
| frontier_asic_constant_main | 48 | 2021_2023 | 36 | -0.0466 | 0.0060 | -0.8328 | 0.6667 | 0.5556 | 0.5278 |
| frontier_asic_constant_main | 48 | 2024_2025 | 24 | -0.0923 | 0.0663 | -0.7812 | 0.8333 | 0.3750 | 0.8333 |
| frontier_asic_constant_main | 36 | through_2020 | 49 | -0.0738 | 0.2243 | -1.1319 | 0.3878 | 0.9388 | 0.8980 |
| frontier_asic_constant_main | 36 | 2021_2023 | 36 | -0.0708 | -0.0091 | 0.1694 | 0.7778 | 0.2222 | 0.1389 |
| frontier_asic_constant_main | 36 | 2024_2025 | 24 | -0.0426 | 0.1860 | -0.9943 | 0.2500 | 0.8750 | 0.6250 |
| weighted_baseline_parsimonious_constant | 48 | through_2020 | 78 | -0.1118 | -0.0140 | 0.4218 | 0.8718 | 0.4615 | 0.4487 |
| weighted_baseline_parsimonious_constant | 48 | 2021_2023 | 36 | -0.0788 | 0.0072 | -0.8233 | 0.9444 | 0.3889 | 0.5556 |
| weighted_baseline_parsimonious_constant | 48 | 2024_2025 | 24 | -0.0736 | 0.0720 | -0.7184 | 0.5833 | 0.5000 | 0.8750 |
| weighted_baseline_parsimonious_constant | 36 | through_2020 | 90 | -0.1284 | 0.0463 | -0.2585 | 0.8222 | 0.5222 | 0.5333 |
| weighted_baseline_parsimonious_constant | 36 | 2021_2023 | 36 | -0.0898 | -0.0103 | 1.2677 | 0.8333 | 0.2778 | 0.3056 |
| weighted_baseline_parsimonious_constant | 36 | 2024_2025 | 24 | -0.0328 | 0.1920 | -0.9877 | 0.2500 | 0.8333 | 0.7083 |
| frontier_baseline_none_sensitivity | 48 | through_2020 | 78 | -0.0350 | 0.0398 | -0.2666 | 0.5769 | 0.4615 | 0.5000 |
| frontier_baseline_none_sensitivity | 48 | 2021_2023 | 36 | -0.0603 | -0.0164 | -0.3951 | 0.7222 | 0.0833 | 0.0278 |
| frontier_baseline_none_sensitivity | 48 | 2024_2025 | 24 | -0.0682 | 0.0572 | -0.3839 | 0.4167 | 0.2083 | 0.7917 |
| frontier_baseline_none_sensitivity | 36 | through_2020 | 90 | -0.0764 | 0.0953 | -0.2627 | 0.6778 | 0.4778 | 0.5889 |
| frontier_baseline_none_sensitivity | 36 | 2021_2023 | 36 | -0.0719 | -0.0183 | -0.3941 | 0.8611 | 0.0278 | 0.1944 |
| frontier_baseline_none_sensitivity | 36 | 2024_2025 | 24 | -0.0373 | 0.0366 | -0.3758 | 0.4167 | 0.3750 | 0.5417 |
| weighted_asic_linear_trend_sensitivity | 48 | through_2020 | 37 | -0.0537 | 0.1557 | -0.2445 | 0.8108 | 0.6757 | 1.0000 |
| weighted_asic_linear_trend_sensitivity | 48 | 2021_2023 | 36 | -0.1159 | -0.0270 | -0.3332 | 1.0000 | 0.0833 | 0.1111 |
| weighted_asic_linear_trend_sensitivity | 48 | 2024_2025 | 24 | -0.0799 | 0.0625 | -0.3714 | 0.7917 | 0.5000 | 0.6667 |
| weighted_asic_linear_trend_sensitivity | 36 | through_2020 | 49 | -0.0824 | 0.1706 | -0.2819 | 0.8367 | 0.6531 | 0.9796 |
| weighted_asic_linear_trend_sensitivity | 36 | 2021_2023 | 36 | -0.1131 | -0.0266 | -0.3622 | 1.0000 | 0.0278 | 0.2778 |
| weighted_asic_linear_trend_sensitivity | 36 | 2024_2025 | 24 | -0.1619 | 0.1492 | -0.3541 | 0.7083 | 0.6667 | 0.7917 |

## Basic Interpretation

The rolling VECM results should be judged against the earlier static evidence. If the frontier ASIC-era model shows persistent cost-side adjustment across windows, it reinforces the static VECM reading that the constructed frontier MCI adjusts to disequilibrium more clearly than price. If the strength or sign of adjustment changes across windows, that supports the Gregory-Hansen conclusion that the long-run price-cost relation is structurally unstable.

For the main frontier ASIC-era model with 48-month windows, cost adjustment is significant at 5% in 68.0% of windows, price adjustment is significant at 10% in 47.4% of windows, and opposite-sign alphas occur in 64.9% of windows. The median cost alpha is 0.0779, while the median price alpha is -0.0515.
The median rolling cost coefficient is -0.9971, which is close to the static ASIC-era value when summarized by the median, but the min-max range is wide. This means the central tendency remains economically plausible while individual windows can be unstable.
For the main frontier ASIC-era model with 36-month windows, cost adjustment is significant at 5% in 68.8% of windows, price adjustment is significant at 10% in 48.6% of windows, and opposite-sign alphas occur in 58.7% of windows. The median cost alpha is 0.1769, while the median price alpha is -0.0663.
The median rolling cost coefficient is -1.0516, which is close to the static ASIC-era value when summarized by the median, but the min-max range is wide. This means the central tendency remains economically plausible while individual windows can be unstable.

The regime split sharpens the interpretation.
For 48-month frontier ASIC windows, cost adjustment is strongest before 2021 (100.0% of windows significant at 5%, median cost alpha 0.2760). It weakens in windows ending during 2021-2023 (55.6%, median cost alpha 0.0060), then partially reappears in 2024-2025 (37.5%, median cost alpha 0.0663).
For 36-month frontier ASIC windows, cost adjustment is strongest before 2021 (93.9% of windows significant at 5%, median cost alpha 0.2243). It weakens in windows ending during 2021-2023 (22.2%, median cost alpha -0.0091), then partially reappears in 2024-2025 (87.5%, median cost alpha 0.1860).

The main conclusion is therefore nuanced. Rolling estimates do not overturn the static frontier ASIC result; they show that cost-side adjustment is a recurrent feature. But the effect is not stable across regimes, especially in windows ending in 2021-2023. This is consistent with the Gregory-Hansen evidence that the long-run relation is structurally unstable and with the static VECM interpretation that RQ3 should not be answered as a simple, permanent cost-anchor mechanism.

Weighted rolling results remain secondary. They are useful for checking whether price-leading-cost dynamics recur, but they should not overturn the main conclusion because the static weighted baseline had an economically awkward vector, residual autocorrelation, and same-sign alpha behavior.

## Figure

- Main rolling VECM figure: `outputs/figures/rolling_vecm_combined_frontier_weighted_r.png`

## Full Rolling Results

The complete window-level estimates are stored in `outputs/tables/rolling_vecm_coefficients.csv`.
