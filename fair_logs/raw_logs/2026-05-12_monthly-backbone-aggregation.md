## FAIR LOG

Date: 2026-05-12
Tool: Codex
Model: GPT-5
Purpose: Aggregate the cleaned daily backbone to monthly frequency for thesis marginal-cost and econometric construction.

### Prompt

start with this

Selected text: Aggregate the daily backbone to monthly.

### Output (condensed)

Created `scripts/07_aggregate_monthly_backbone.py` to aggregate `backbone_daily_merged.csv` to monthly frequency. The script computes monthly average Bitcoin price and difficulty, monthly sums of blocks, fees, issuance, and miner compensation, and monthly miner compensation per block. It writes `backbone_monthly.csv`, `backbone_monthly_audit.csv`, and `backbone_monthly_audit.md`. Updated `wiki/data.md`, `wiki/Tasks.md`, and `wiki/model.md` to document the monthly backbone outputs and remaining variables.

### Usage

Used.

This interaction creates the monthly backbone inputs needed before hardware-efficiency path construction and marginal-cost index construction.

### Reference

File name: 2026-05-12_monthly-backbone-aggregation.md
