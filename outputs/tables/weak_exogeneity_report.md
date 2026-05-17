# Weak-Exogeneity Tests

Purpose: formally test whether Bitcoin price and the marginal-cost measure adjust to the cointegrating relation.

Implementation:

- Individual weak-exogeneity restrictions use `urca::alrtest()` on `ca.jo` objects.
- The null `alpha_price = 0` tests whether Bitcoin price is weakly exogenous.
- The null `alpha_cost = 0` tests whether the MCI is weakly exogenous.
- The joint no-adjustment test is reported as the Johansen rank-zero/no-error-correction trace LR test, because imposing both alpha coefficients equal to zero collapses `alpha beta'` to zero.
- Static systems only; no rolling or regime split tests are run.

## Main Results

| specification | restriction | null_hypothesis | test_family | lr_statistic | df | p_value | critical_5pct | reject_5pct | interpretation |
|---|---|---|---|---|---|---|---|---|---|
| frontier_asic_constant_main | price_weakly_exogenous | alpha_price = 0 | Johansen alpha-restriction LR | 2.6300 | 1.0000 | 0.1049 | NA | FALSE | Do not reject price weak exogeneity at 5%. |
| frontier_asic_constant_main | cost_weakly_exogenous | alpha_cost = 0 | Johansen alpha-restriction LR | 24.4744 | 1.0000 | 0.0000 | NA | TRUE | Reject cost weak exogeneity at 5%; cost adjusts. |
| frontier_asic_constant_main | joint_no_error_correction | alpha_price = alpha_cost = 0 / no error-correction term | Johansen trace rank-zero LR | 41.4172 | 2.0000 | NA | 19.9600 | TRUE | Reject no error correction at 5%; at least one variable adjusts. |
| weighted_baseline_parsimonious_constant | price_weakly_exogenous | alpha_price = 0 | Johansen alpha-restriction LR | 14.8260 | 1.0000 | 1e-04 | NA | TRUE | Reject price weak exogeneity at 5%; price adjusts. |
| weighted_baseline_parsimonious_constant | cost_weakly_exogenous | alpha_cost = 0 | Johansen alpha-restriction LR | 12.6025 | 1.0000 | 4e-04 | NA | TRUE | Reject cost weak exogeneity at 5%; cost adjusts. |
| weighted_baseline_parsimonious_constant | joint_no_error_correction | alpha_price = alpha_cost = 0 / no error-correction term | Johansen trace rank-zero LR | 27.9329 | 2.0000 | NA | 19.9600 | TRUE | Reject no error correction at 5%; at least one variable adjusts. |
| weighted_asic_linear_trend_sensitivity | price_weakly_exogenous | alpha_price = 0 | Johansen alpha-restriction LR | 14.1893 | 1.0000 | 2e-04 | NA | TRUE | Reject price weak exogeneity at 5%; price adjusts. |
| weighted_asic_linear_trend_sensitivity | cost_weakly_exogenous | alpha_cost = 0 | Johansen alpha-restriction LR | 0.2206 | 1.0000 | 0.6386 | NA | FALSE | Do not reject cost weak exogeneity at 5%. |
| weighted_asic_linear_trend_sensitivity | joint_no_error_correction | alpha_price = alpha_cost = 0 / no error-correction term | Johansen trace rank-zero LR | 21.1285 | 2.0000 | NA | 25.3200 | FALSE | Do not reject no error correction at 5%. |
| frontier_baseline_none_sensitivity | price_weakly_exogenous | alpha_price = 0 | Johansen alpha-restriction LR | 8.8629 | 1.0000 | 0.0029 | NA | TRUE | Reject price weak exogeneity at 5%; price adjusts. |
| frontier_baseline_none_sensitivity | cost_weakly_exogenous | alpha_cost = 0 | Johansen alpha-restriction LR | 0.0095 | 1.0000 | 0.9224 | NA | FALSE | Do not reject cost weak exogeneity at 5%. |
| frontier_baseline_none_sensitivity | joint_no_error_correction | alpha_price = alpha_cost = 0 / no error-correction term | Johansen trace rank-zero LR | 35.5536 | 2.0000 | NA | 17.9500 | TRUE | Reject no error correction at 5%; at least one variable adjusts. |

## Alpha/Beta Snapshot From `urca::ca.jo`

| specification | system | sample | sample_start | sample_end | nobs_levels | K_var_lag_order_levels | rank | ecdet | ca_jo_spec | role | alpha_price_urca | alpha_cost_urca | beta_price_urca | beta_cost_urca | same_sign_alpha | opposite_sign_alpha |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| frontier_asic_constant_main | frontier | asic_robustness_2014_01 | 2014-01-01 | 2025-12-01 | 144.0000 | 2.0000 | 1.0000 | const | longrun | main frontier ASIC-era weak-exogeneity test | -0.0457 | 0.1563 | 1.0000 | -0.9429 | FALSE | TRUE |
| weighted_baseline_parsimonious_constant | weighted | baseline_2010_08 | 2010-08-01 | 2025-12-01 | 185.0000 | 2.0000 | 1.0000 | const | longrun | weighted baseline complementary RQ3 test; interpret with vector/sign-condition caveats | -0.0012 | -0.0014 | 1.0000 | 16.2647 | TRUE | FALSE |
| weighted_asic_linear_trend_sensitivity | weighted | asic_robustness_2014_01 | 2014-01-01 | 2025-12-01 | 144.0000 | 2.0000 | 1.0000 | trend | longrun | weighted ASIC-era trend sensitivity | -0.1025 | 0.0274 | 1.0000 | 0.5072 | FALSE | TRUE |
| frontier_baseline_none_sensitivity | frontier | baseline_2010_08 | 2010-08-01 | 2025-12-01 | 185.0000 | 2.0000 | 1.0000 | none | longrun | frontier full-sample instability sensitivity | -0.0946 | 0.0041 | 1.0000 | -0.6700 | FALSE | TRUE |

## Interpretation Note

For the main frontier ASIC-era system, the cleanest pattern would be: reject the joint no-error-correction restriction, fail to reject `alpha_price = 0`, and reject `alpha_cost = 0`. That combination supports one adjusting variable, with adjustment occurring through the frontier MCI rather than Bitcoin price.

The main frontier ASIC-era system shows exactly this clean pattern: price weak exogeneity is not rejected, cost weak exogeneity is rejected, and the joint no-error-correction restriction is rejected. This formally supports the static and rolling interpretation that, in the cleanest frontier system, the frontier MCI is the adjusting variable.

The weighted baseline rejects both individual weak-exogeneity restrictions and rejects the joint no-error-correction restriction. This supports the rolling result that weighted systems contain price-side adjustment, but it does not remove the earlier limitations: the static weighted baseline has a same-sign alpha problem, residual autocorrelation, and an economically awkward vector.

The weighted ASIC trend and full-sample frontier no-deterministic sensitivity systems are included for completeness, but they should be read cautiously because deterministic-term handling differs across VECM implementations and these systems were already classified as sensitivity/instability cases.

## Full CSV Outputs

- `outputs/tables/weak_exogeneity_tests.csv`
- `outputs/tables/weak_exogeneity_alpha_beta_snapshot.csv`
- `outputs/tables/weak_exogeneity_interpretation.csv`
