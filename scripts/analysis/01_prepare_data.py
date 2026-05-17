from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml


CUTOFF_DATE = pd.Timestamp("2025-12-31")
ANALYSIS_START_DATE = pd.Timestamp("2010-08-01")


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "config" / "paths.yaml"
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def output_dir(config: dict) -> Path:
    path = Path(config["paths"]["processed_data"]) / "backbone"
    path.mkdir(parents=True, exist_ok=True)
    return path


def raw_dir(config: dict) -> Path:
    return Path(config["paths"]["raw_data"])


def trim_to_cutoff(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col]).dt.normalize()
    return df.loc[df[date_col] <= CUTOFF_DATE].sort_values(date_col).reset_index(drop=True)


def clean_bitcoinity(base: Path) -> pd.DataFrame:
    path = base / "bitcoinity_data_price.csv"
    df = pd.read_csv(path)
    exchange_cols = [c for c in df.columns if c != "Time"]

    df["date"] = pd.to_datetime(df["Time"], utc=True, errors="coerce").dt.tz_convert(None).dt.normalize()
    df["btc_price_usd"] = df[exchange_cols].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    df = df.loc[:, ["date", "btc_price_usd"]]
    df = df.dropna(subset=["date"]).drop_duplicates(subset=["date"], keep="last")
    return trim_to_cutoff(df)


def clean_coinmetrics(base: Path) -> pd.DataFrame:
    path = base / "coinmetrics_btc_community.csv"
    cols = ["time", "BlkCnt", "FeeTotNtv", "IssTotNtv", "PriceUSD"]
    df = pd.read_csv(path, usecols=cols)
    rename_map = {
        "time": "date",
        "BlkCnt": "blk_cnt",
        "FeeTotNtv": "fee_tot_ntv",
        "IssTotNtv": "iss_tot_ntv",
        "PriceUSD": "price_usd_coinmetrics",
    }
    df = df.rename(columns=rename_map)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["blk_cnt", "fee_tot_ntv", "iss_tot_ntv", "price_usd_coinmetrics"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    zero_block_mask = df["blk_cnt"].fillna(0).eq(0)
    df.loc[zero_block_mask & df["iss_tot_ntv"].isna(), "iss_tot_ntv"] = 0.0

    df["rev_ntv"] = df[["fee_tot_ntv", "iss_tot_ntv"]].sum(axis=1, min_count=1)
    df["rev_usd"] = df["rev_ntv"] * df["price_usd_coinmetrics"]
    df["subsidy_per_block_implied"] = df["iss_tot_ntv"] / df["blk_cnt"].where(df["blk_cnt"] > 0)
    df = df.dropna(subset=["date"]).drop_duplicates(subset=["date"], keep="last")
    return trim_to_cutoff(df)


def clean_difficulty(base: Path) -> pd.DataFrame:
    path = base / "difficulty_blockchain_api_sampled-false.json"
    data = json.loads(path.read_text())
    df = pd.DataFrame(data["values"])
    df["date"] = pd.to_datetime(df["x"], unit="s", errors="coerce")
    df["difficulty"] = pd.to_numeric(df["y"], errors="coerce")
    df = df.loc[:, ["date", "difficulty"]]
    df = df.dropna(subset=["date"]).drop_duplicates(subset=["date"], keep="last")
    df = trim_to_cutoff(df)

    full_dates = pd.DataFrame({"date": pd.date_range(df["date"].min(), df["date"].max(), freq="D")})
    df = full_dates.merge(df, on="date", how="left")
    df["difficulty"] = df["difficulty"].interpolate(method="linear", limit_direction="both")
    return df


def clean_bitcoinvisuals(base: Path) -> pd.DataFrame:
    path = base / "BitcoinVisuals.com_chart.csv"
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    df.columns = [c.strip('"') for c in df.columns]
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip('"')

    df["date"] = pd.to_datetime(df["DateTime"], errors="coerce")
    df["subsidy_btc_visuals"] = pd.to_numeric(
        df["BTC"].str.replace(",", ".", regex=False),
        errors="coerce",
    )
    df["subsidy_usd_visuals"] = pd.to_numeric(
        df["USD"].str.replace(",", ".", regex=False),
        errors="coerce",
    )
    df = df.loc[:, ["date", "subsidy_btc_visuals", "subsidy_usd_visuals"]]
    df = df.dropna(subset=["date"]).drop_duplicates(subset=["date"], keep="last")
    return trim_to_cutoff(df)


def build_validation_table(
    coinmetrics_df: pd.DataFrame,
    visuals_df: pd.DataFrame,
) -> pd.DataFrame:
    df = coinmetrics_df.merge(visuals_df, on="date", how="left")
    df["subsidy_abs_diff"] = (
        df["subsidy_per_block_implied"] - df["subsidy_btc_visuals"]
    ).abs()
    return df


def build_backbone_daily(
    price_df: pd.DataFrame,
    coinmetrics_df: pd.DataFrame,
    difficulty_df: pd.DataFrame,
    visuals_df: pd.DataFrame,
) -> pd.DataFrame:
    merged = price_df.merge(coinmetrics_df, on="date", how="outer")
    merged = merged.merge(difficulty_df, on="date", how="outer")
    merged = merged.merge(visuals_df, on="date", how="outer")
    merged = merged.sort_values("date").reset_index(drop=True)
    merged["analysis_sample"] = merged["date"] >= ANALYSIS_START_DATE
    merged = merged.rename(
        columns={
            "btc_price_usd": "bitcoin_market_price_usd",
            "blk_cnt": "blocks_mined",
            "fee_tot_ntv": "total_transaction_fees_btc",
            "iss_tot_ntv": "new_coins_issued_btc",
            "price_usd_coinmetrics": "coinmetrics_bitcoin_price_usd",
            "rev_ntv": "total_miner_compensation_btc",
            "rev_usd": "total_miner_compensation_usd",
            "subsidy_per_block_implied": "implied_block_subsidy_btc",
            "difficulty": "network_difficulty",
            "subsidy_btc_visuals": "bitcoinvisuals_block_subsidy_btc",
            "subsidy_usd_visuals": "bitcoinvisuals_block_subsidy_usd",
        }
    )
    return trim_to_cutoff(merged)


def dataset_audit(df: pd.DataFrame, name: str, date_col: str = "date") -> dict:
    audit = {"dataset": name, "rows": int(len(df))}
    if df.empty:
        audit.update(
            {
                "min_date": None,
                "max_date": None,
                "duplicate_dates": 0,
                "missing_dates_inside_span": 0,
            }
        )
        return audit

    dates = pd.to_datetime(df[date_col]).dropna().sort_values()
    span = pd.date_range(dates.min(), dates.max(), freq="D")
    audit.update(
        {
            "min_date": dates.min().date().isoformat(),
            "max_date": dates.max().date().isoformat(),
            "duplicate_dates": int(df[date_col].duplicated().sum()),
            "missing_dates_inside_span": int(len(span.difference(dates))),
        }
    )
    for col in df.columns:
        if col != date_col:
            audit[f"missing_{col}"] = int(df[col].isna().sum())
    return audit


def write_audit_md(audit_df: pd.DataFrame, output_path: Path) -> None:
    lines = ["# Backbone Daily Audit", "", f"Cutoff date: `{CUTOFF_DATE.date().isoformat()}`", ""]
    for _, row in audit_df.iterrows():
        lines.append(f"## {row['dataset']}")
        lines.append("")
        for col, value in row.items():
            if col == "dataset":
                continue
            lines.append(f"- `{col}`: {value}")
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    config = load_config()
    raw = raw_dir(config)
    out = output_dir(config)

    price_df = clean_bitcoinity(raw)
    coinmetrics_df = clean_coinmetrics(raw)
    difficulty_df = clean_difficulty(raw)
    visuals_df = clean_bitcoinvisuals(raw)
    validation_df = build_validation_table(coinmetrics_df, visuals_df)
    backbone_df = build_backbone_daily(price_df, coinmetrics_df, difficulty_df, visuals_df)

    price_df.to_csv(out / "bitcoinity_price_daily_clean.csv", index=False)
    coinmetrics_df.to_csv(out / "coinmetrics_btc_daily_clean.csv", index=False)
    difficulty_df.to_csv(out / "difficulty_daily_clean.csv", index=False)
    visuals_df.to_csv(out / "bitcoinvisuals_subsidy_daily_check.csv", index=False)
    validation_df.to_csv(out / "coinmetrics_vs_bitcoinvisuals_validation.csv", index=False)
    backbone_df.to_csv(out / "backbone_daily_merged.csv", index=False)

    audits = pd.DataFrame(
        [
            dataset_audit(price_df, "bitcoinity_price_daily_clean"),
            dataset_audit(coinmetrics_df, "coinmetrics_btc_daily_clean"),
            dataset_audit(difficulty_df, "difficulty_daily_clean"),
            dataset_audit(visuals_df, "bitcoinvisuals_subsidy_daily_check"),
            dataset_audit(backbone_df, "backbone_daily_merged"),
        ]
    )
    audits.to_csv(out / "backbone_daily_audit.csv", index=False)
    write_audit_md(audits, out / "backbone_daily_audit.md")

    print(f"Wrote cleaned backbone files to {out}")
    print("Created:")
    for file_name in [
        "bitcoinity_price_daily_clean.csv",
        "coinmetrics_btc_daily_clean.csv",
        "difficulty_daily_clean.csv",
        "bitcoinvisuals_subsidy_daily_check.csv",
        "coinmetrics_vs_bitcoinvisuals_validation.csv",
        "backbone_daily_merged.csv",
        "backbone_daily_audit.csv",
        "backbone_daily_audit.md",
    ]:
        print(f"- {out / file_name}")


if __name__ == "__main__":
    main()
