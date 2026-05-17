## FAIR LOG

Date: 2026-05-13
Tool: Codex
Model: GPT-5
Purpose: Run Johansen cointegration tests for the weighted and frontier marginal-cost systems.

### Prompt

User asked to proceed with Johansen testing after documenting the integration-order decision.

### Output (condensed)

Created and ran `scripts/13_johansen_cointegration.py`. The script tests bivariate systems pairing log Bitcoin price with log weighted MCI and log frontier MCI. It runs the baseline `2010-08` sample and the pre-planned `2014-01` ASIC-period robustness sample, selects VAR lag order on levels, runs Johansen trace and maximum-eigenvalue tests, records deterministic-term sensitivity, and adds lag-criterion sensitivity across AIC/BIC/HQIC/FPE. Outputs were written to `outputs/tables`. Results are mixed: AIC/constant does not support weighted baseline cointegration, while BIC/HQIC/constant does; frontier baseline gives rank 2 under constant/trend but rank 1 without deterministic terms; frontier 2014 robustness cleanly supports rank 1 under constant/trend. Documentation was updated to preserve this specification-sensitive interpretation.

### Usage

Used.

This interaction supplies the first cointegration test evidence for the thesis and determines which candidate systems should be carried forward to VECM estimation with careful specification labels.

### Reference

File name: 2026-05-13_johansen-cointegration-tests.md
