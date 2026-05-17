## FAIR LOG

Date: 2026-05-13
Tool: Codex
Model: GPT-5
Purpose: Run Gregory-Hansen structural-break cointegration tests in R.

### Prompt

User asked to run Gregory-Hansen testing and noted that R is installed locally. Earlier project notes specified that Gregory-Hansen should be run in R because Python lacks a reliable implementation.

### Output (condensed)

Installed the required R packages (`COINT`, `urca`, `cointReg`, and dependencies), confirmed that `urca::ca.po()` is Phillips-Ouliaris rather than Gregory-Hansen, and used `COINT::GHansen()` for the Gregory-Hansen tests. Created `scripts/14_gregory_hansen_tests.R` and ran tests for weighted and frontier MCI systems over the baseline `2010-08` sample and the `2014-01` ASIC robustness sample. Tested the four COINT model forms (level shift, level shift with trend, regime shift, regime plus trend shift), and wrote full results, strongest-test summaries, model summaries, system summaries, and a Markdown report to `outputs/tables`. At least one 5 percent rejection was found for every system/sample combination, with break dates varying by model and test family.

### Usage

Used.

This interaction provides the structural-break cointegration robustness evidence needed after the specification-sensitive Johansen results.

### Reference

File name: 2026-05-13_gregory-hansen-tests.md
