from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml


HASHES_PER_DIFFICULTY = 2**32
HASHES_PER_TH = 10**12
ANALYSIS_START_MONTH = pd.Timestamp("2010-08-01")


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "config" / "paths.yaml"
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def processed_dir(config: dict) -> Path:
    return Path(config["paths"]["processed_data"])


def read_monthly_inputs(processed: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    backbone = pd.read_csv(processed / "backbone" / "backbone_monthly.csv")
    frontier = pd.read_csv(processed / "hardware" / "frontier_efficiency_monthly.csv")
    weighted = pd.read_csv(processed / "hardware" / "weighted_efficiency_monthly.csv")

    for df in [backbone, frontier, weighted]:
        df["month"] = pd.to_datetime(df["month"])

    return backbone, frontier, weighted


def construct_panel(
    backbone: pd.DataFrame,
    frontier: pd.DataFrame,
    weighted: pd.DataFrame,
) -> pd.DataFrame:
    weighted = weighted.rename(columns={"eta_weighted_avg": "eta_weighted_avg_j_per_th"})
    panel = backbone.merge(
        frontier[
            [
                "month",
                "frontier_efficiency_j_per_th",
                "frontier_hardware_model",
                "frontier_hardware_type",
                "frontier_release_date",
                "frontier_changed",
            ]
        ],
        on="month",
        how="left",
    )
    panel = panel.merge(
        weighted[
            [
                "month",
                "eta_weighted_avg_j_per_th",
                "n_active_devices",
                "sum_weights",
            ]
        ],
        on="month",
        how="left",
    )

    panel["energy_per_block_frontier_j"] = (
        panel["frontier_efficiency_j_per_th"]
        * panel["network_difficulty_monthly"]
        * HASHES_PER_DIFFICULTY
        / HASHES_PER_TH
    )
    panel["energy_per_block_weighted_j"] = (
        panel["eta_weighted_avg_j_per_th"]
        * panel["network_difficulty_monthly"]
        * HASHES_PER_DIFFICULTY
        / HASHES_PER_TH
    )
    panel["mci_frontier_j_per_btc"] = (
        panel["energy_per_block_frontier_j"]
        / panel["miner_compensation_per_block_btc_monthly"]
    )
    panel["mci_weighted_j_per_btc"] = (
        panel["energy_per_block_weighted_j"]
        / panel["miner_compensation_per_block_btc_monthly"]
    )

    panel["analysis_sample"] = panel["month"] >= ANALYSIS_START_MONTH
    panel["log_bitcoin_market_price_usd"] = np.log(panel["bitcoin_market_price_usd_monthly"])
    panel["log_mci_frontier"] = np.log(panel["mci_frontier_j_per_btc"])
    panel["log_mci_weighted"] = np.log(panel["mci_weighted_j_per_btc"])

    return panel.sort_values("month").reset_index(drop=True)


def nonpositive_count(series: pd.Series) -> int:
    return int(pd.to_numeric(series, errors="coerce").le(0).sum())


def audit_panel(panel: pd.DataFrame) -> dict:
    analysis = panel.loc[panel["analysis_sample"]].copy()
    expected_months = pd.date_range(panel["month"].min(), panel["month"].max(), freq="MS")
    key_cols = [
        "bitcoin_market_price_usd_monthly",
        "network_difficulty_monthly",
        "miner_compensation_per_block_btc_monthly",
        "frontier_efficiency_j_per_th",
        "eta_weighted_avg_j_per_th",
        "mci_frontier_j_per_btc",
        "mci_weighted_j_per_btc",
        "log_bitcoin_market_price_usd",
        "log_mci_frontier",
        "log_mci_weighted",
    ]
    audit = {
        "rows": int(len(panel)),
        "min_month": panel["month"].min().date().isoformat(),
        "max_month": panel["month"].max().date().isoformat(),
        "missing_months_inside_span": int(len(expected_months.difference(panel["month"]))),
        "analysis_rows": int(len(analysis)),
        "analysis_min_month": analysis["month"].min().date().isoformat(),
        "analysis_max_month": analysis["month"].max().date().isoformat(),
    }
    for col in key_cols:
        audit[f"analysis_missing_{col}"] = int(analysis[col].isna().sum())
        if col.startswith("log_"):
            audit[f"analysis_nonfinite_{col}"] = int((~np.isfinite(analysis[col])).sum())
        else:
            audit[f"analysis_nonpositive_{col}"] = nonpositive_count(analysis[col])
    return audit


def write_audit_md(audit: dict, output_path: Path) -> None:
    lines = [
        "# Monthly Master Panel Audit",
        "",
        "Sources:",
        "",
        "- `data/processed/backbone/backbone_monthly.csv`",
        "- `data/processed/hardware/frontier_efficiency_monthly.csv`",
        "- `data/processed/hardware/weighted_efficiency_monthly.csv`",
        "",
        "Formula implementation:",
        "",
        "- `miner_compensation_per_block_btc_monthly = total_miner_compensation_btc_monthly / blocks_mined_monthly`",
        "- `energy_per_block_j = eta_j_per_th * network_difficulty_monthly * 2^32 / 10^12`",
        "- `mci_j_per_btc = energy_per_block_j / miner_compensation_per_block_btc_monthly`",
        "",
        f"- `HASHES_PER_DIFFICULTY`: {HASHES_PER_DIFFICULTY}",
        f"- `HASHES_PER_TH`: {HASHES_PER_TH}",
        "",
    ]
    for key, value in audit.items():
        lines.append(f"- `{key}`: {value}")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    config = load_config()
    processed = processed_dir(config)
    out = processed / "monthly"
    out.mkdir(parents=True, exist_ok=True)

    backbone, frontier, weighted = read_monthly_inputs(processed)
    panel = construct_panel(backbone, frontier, weighted)
    audit = audit_panel(panel)

    panel.to_csv(out / "monthly_master_panel.csv", index=False)
    pd.DataFrame([audit]).to_csv(out / "monthly_master_panel_audit.csv", index=False)
    write_audit_md(audit, out / "monthly_master_panel_audit.md")

    print(f"Wrote monthly master panel files to {out}")
    print("Created:")
    for file_name in [
        "monthly_master_panel.csv",
        "monthly_master_panel_audit.csv",
        "monthly_master_panel_audit.md",
    ]:
        print(f"- {out / file_name}")


if __name__ == "__main__":
    main()
