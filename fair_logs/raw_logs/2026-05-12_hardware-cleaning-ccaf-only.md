## FAIR LOG

Date: 2026-05-12
Tool: Codex
Model: GPT-5
Purpose: Clean the CCAF/CBECI hardware source as the sole active hardware dataset and document the decision not to enrich from other local hardware files.

### Prompt

Okay update the documentation and clean, convert and truncate Mining equipment list - list.csv. For the 'Type' column, it is very safe to assume that all models released after 2013 are ASIC. The literature doesn't mention any other type of hardware besides ASIC. so fill in that column

### Output (condensed)

Created `scripts/06_prepare_hardware.py` to clean `Mining equipment list - list.csv`, strip metadata rows, standardize numeric fields, convert efficiency from `J/Gh` to `J/TH`, fill missing post-2013 hardware types as `ASIC`, and truncate releases after `2025-12-31`. Wrote cleaned outputs to `data/processed/hardware/`: `hardware_master_clean.csv`, `hardware_master_audit.csv`, and `hardware_master_audit.md`. Updated `wiki/data.md`, `wiki/Tasks.md`, and `wiki/decisions.md` to document the CCAF/CBECI-only hardware source rule and the post-2013 ASIC fill assumption.

### Usage

Used.

This interaction produces the cleaned hardware master table that will support the frontier and weighted-average hardware-efficiency paths in the thesis marginal-cost construction.

### Reference

File name: 2026-05-12_hardware-cleaning-ccaf-only.md
