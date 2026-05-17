# FAIR Raw Log: Weak-Exogeneity Tests

## Metadata

- Date: 2026-05-14
- Tool / model: Codex / GPT-5
- Project: Master thesis Bitcoin marginal-cost analysis

## Prompt Summary

The user asked to run weak-exogeneity tests after the rolling VECM analysis, adding a joint test of `alpha_price = alpha_mci = 0` and explicitly declining optional rolling/regime-split weak-exogeneity tests.

## Actions Taken

- Created `scripts/18_weak_exogeneity_tests.R`.
- Used `urca::alrtest()` for individual Johansen alpha-restriction LR tests.
- Reported the joint no-adjustment restriction as the Johansen rank-zero/no-error-correction trace LR test.
- Ran static tests for the main frontier ASIC-era system and selected weighted/frontier sensitivity systems.
- Wrote outputs to `outputs/tables`.
- Updated `wiki/econometrics.md`, `wiki/next_session_handoff.md`, and `wiki/Tasks.md`.

## Outputs Created

- `outputs/tables/weak_exogeneity_tests.csv`
- `outputs/tables/weak_exogeneity_alpha_beta_snapshot.csv`
- `outputs/tables/weak_exogeneity_interpretation.csv`
- `outputs/tables/weak_exogeneity_report.md`

## Thesis Use

Use these tests for RQ3. They provide formal statistical support for the main frontier interpretation and clarify how weighted-system price adjustment should be treated as complementary evidence rather than as the primary adjustment model.
