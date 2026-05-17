from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


ANALYSIS_START_MONTH = pd.Timestamp("2010-08-01")


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "config" / "paths.yaml"
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def backbone_dir(config: dict) -> Path:
    return Path(config["paths"]["processed_data"]) / "backbone"


def month_start(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.to_period("M").dt.to_timestamp()


def aggregate_monthly(daily_df: pd.DataFrame) -> pd.DataFrame:
    df = daily_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = month_start(df["date"])

    grouped = df.groupby("month", as_index=False)
    monthly = grouped.agg(
        bitcoin_market_price_usd_monthly=("bitcoin_market_price_usd", "mean"),
        network_difficulty_monthly=("network_difficulty", "mean"),
        blocks_mined_monthly=("blocks_mined", "sum"),
        total_transaction_fees_btc_monthly=("total_transaction_fees_btc", "sum"),
        new_coins_issued_btc_monthly=("new_coins_issued_btc", "sum"),
        total_miner_compensation_btc_monthly=("total_miner_compensation_btc", "sum"),
        total_miner_compensation_usd_monthly=("total_miner_compensation_usd", "sum"),
        implied_block_subsidy_btc_monthly=("implied_block_subsidy_btc", "mean"),
        coinmetrics_bitcoin_price_usd_monthly=("coinmetrics_bitcoin_price_usd", "mean"),
        bitcoinvisuals_block_subsidy_btc_monthly=("bitcoinvisuals_block_subsidy_btc", "mean"),
        daily_observations=("date", "count"),
        price_observation_days=("bitcoin_market_price_usd", "count"),
        difficulty_observation_days=("network_difficulty", "count"),
        blocks_observation_days=("blocks_mined", "count"),
        compensation_observation_days=("total_miner_compensation_btc", "count"),
    )

    monthly["calendar_days_in_month"] = monthly["month"].dt.days_in_month
    monthly["miner_compensation_per_block_btc_monthly"] = (
        monthly["total_miner_compensation_btc_monthly"]
        / monthly["blocks_mined_monthly"].where(monthly["blocks_mined_monthly"] > 0)
    )
    monthly["analysis_sample"] = monthly["month"] >= ANALYSIS_START_MONTH
    monthly["complete_price_month"] = (
        monthly["price_observation_days"] == monthly["calendar_days_in_month"]
    )
    monthly["complete_backbone_month"] = (
        (monthly["difficulty_observation_days"] == monthly["calendar_days_in_month"])
        & (monthly["blocks_observation_days"] == monthly["calendar_days_in_month"])
        & (monthly["compensation_observation_days"] == monthly["calendar_days_in_month"])
    )

    ordered_cols = [
        "month",
        "bitcoin_market_price_usd_monthly",
        "network_difficulty_monthly",
        "blocks_mined_monthly",
        "total_transaction_fees_btc_monthly",
        "new_coins_issued_btc_monthly",
        "total_miner_compensation_btc_monthly",
        "total_miner_compensation_usd_monthly",
        "miner_compensation_per_block_btc_monthly",
        "implied_block_subsidy_btc_monthly",
        "coinmetrics_bitcoin_price_usd_monthly",
        "bitcoinvisuals_block_subsidy_btc_monthly",
        "analysis_sample",
        "daily_observations",
        "calendar_days_in_month",
        "price_observation_days",
        "difficulty_observation_days",
        "blocks_observation_days",
        "compensation_observation_days",
        "complete_price_month",
        "complete_backbone_month",
    ]
    return monthly.loc[:, ordered_cols].sort_values("month").reset_index(drop=True)


def audit_monthly(monthly_df: pd.DataFrame) -> dict:
    expected_months = pd.date_range(
        monthly_df["month"].min(),
        monthly_df["month"].max(),
        freq="MS",
    )
    analysis = monthly_df.loc[monthly_df["analysis_sample"]].copy()
    return {
        "rows": int(len(monthly_df)),
        "min_month": monthly_df["month"].min().date().isoformat(),
        "max_month": monthly_df["month"].max().date().isoformat(),
        "missing_months_inside_span": int(
            len(expected_months.difference(monthly_df["month"]))
        ),
        "analysis_rows": int(len(analysis)),
        "analysis_min_month": analysis["month"].min().date().isoformat(),
        "analysis_max_month": analysis["month"].max().date().isoformat(),
        "analysis_missing_price_months": int(
            analysis["bitcoin_market_price_usd_monthly"].isna().sum()
        ),
        "analysis_incomplete_price_months": int(
            (~analysis["complete_price_month"]).sum()
        ),
        "analysis_incomplete_backbone_months": int(
            (~analysis["complete_backbone_month"]).sum()
        ),
        "analysis_missing_miner_compensation_per_block_months": int(
            analysis["miner_compensation_per_block_btc_monthly"].isna().sum()
        ),
    }


def write_audit_md(audit: dict, output_path: Path) -> None:
    lines = [
        "# Backbone Monthly Audit",
        "",
        "Source: `data/processed/backbone/backbone_daily_merged.csv`",
        "",
        "Aggregation rules:",
        "",
        "- Bitcoin market price: monthly arithmetic mean of available daily values",
        "- Network difficulty: monthly arithmetic mean of daily difficulty",
        "- Blocks, fees, issuance, and miner compensation: monthly sums",
        "- Miner compensation per block: monthly miner compensation in BTC divided by monthly blocks mined",
        "- Analysis sample flag: months from `2010-08-01` onward",
        "",
    ]
    for key, value in audit.items():
        lines.append(f"- `{key}`: {value}")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    config = load_config()
    out = backbone_dir(config)
    daily_path = out / "backbone_daily_merged.csv"

    daily_df = pd.read_csv(daily_path)
    monthly_df = aggregate_monthly(daily_df)
    audit = audit_monthly(monthly_df)

    monthly_df.to_csv(out / "backbone_monthly.csv", index=False)
    pd.DataFrame([audit]).to_csv(out / "backbone_monthly_audit.csv", index=False)
    write_audit_md(audit, out / "backbone_monthly_audit.md")

    print(f"Wrote monthly backbone files to {out}")
    print("Created:")
    for file_name in [
        "backbone_monthly.csv",
        "backbone_monthly_audit.csv",
        "backbone_monthly_audit.md",
    ]:
        print(f"- {out / file_name}")


if __name__ == "__main__":
    main()
