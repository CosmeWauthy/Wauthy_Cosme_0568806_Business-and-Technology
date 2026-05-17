from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


DEPLOYMENT_LAG_MONTHS = 2
MAX_ACTIVE_MONTHS = 60


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "config" / "paths.yaml"
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def processed_dir(config: dict) -> Path:
    return Path(config["paths"]["processed_data"])


def month_start(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.to_period("M").dt.to_timestamp()


def add_months(month: pd.Timestamp, months: int) -> pd.Timestamp:
    return (month.to_period("M") + months).to_timestamp()


def months_between(start: pd.Timestamp, end: pd.Timestamp) -> int:
    start_period = start.to_period("M")
    end_period = end.to_period("M")
    return (end_period.year - start_period.year) * 12 + (end_period.month - start_period.month)


def prepare_hardware(hardware: pd.DataFrame) -> pd.DataFrame:
    hw = hardware.copy()
    hw["release_date"] = pd.to_datetime(hw["release_date"])
    hw["release_month"] = month_start(hw["release_date"])
    hw["deployment_month"] = hw["release_month"].map(
        lambda month: add_months(month, DEPLOYMENT_LAG_MONTHS)
    )
    hw = hw.dropna(subset=["deployment_month", "efficiency_j_per_th"])
    return hw.sort_values(["deployment_month", "hardware_model"]).reset_index(drop=True)


def build_weighted_path(monthly_backbone: pd.DataFrame, hardware: pd.DataFrame) -> pd.DataFrame:
    hw = prepare_hardware(hardware)
    first_deployment = hw["deployment_month"].min()
    last_month = pd.to_datetime(monthly_backbone["month"]).max().to_period("M").to_timestamp()
    months = pd.date_range(first_deployment, last_month, freq="MS")

    rows: list[dict] = []
    for month in months:
        active = hw.loc[
            hw["deployment_month"].le(month)
            & hw["deployment_month"].map(lambda deployment: months_between(deployment, month) < MAX_ACTIVE_MONTHS)
        ].copy()

        if active.empty:
            raise ValueError(f"No active hardware devices found for {month.date().isoformat()}")

        active["months_elapsed"] = active["deployment_month"].map(
            lambda deployment: months_between(deployment, month)
        )
        active["year_bucket"] = active["months_elapsed"] // 12
        active["weight"] = 1.0 - active["year_bucket"] * 0.2

        eta_weighted_avg = (
            active["weight"].mul(active["efficiency_j_per_th"]).sum() / active["weight"].sum()
        )
        all_first_year = bool(active["year_bucket"].eq(0).all())

        rows.append(
            {
                "month": month,
                "eta_weighted_avg": eta_weighted_avg,
                "n_active_devices": int(len(active)),
                "sum_weights": float(active["weight"].sum()),
                "all_active_devices_first_year": all_first_year,
            }
        )

    return pd.DataFrame(rows)


def sustained_increase_runs(weighted_df: pd.DataFrame, min_run: int = 3) -> list[tuple[str, str, int]]:
    increases = weighted_df["eta_weighted_avg"].diff().gt(1e-9)
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for idx, increased in enumerate(increases):
        if increased and start is None:
            start = idx
        elif not increased and start is not None:
            if idx - start >= min_run:
                runs.append((start, idx - 1))
            start = None
    if start is not None and len(increases) - start >= min_run:
        runs.append((start, len(increases) - 1))

    return [
        (
            weighted_df.loc[start_idx, "month"].date().isoformat(),
            weighted_df.loc[end_idx, "month"].date().isoformat(),
            int(end_idx - start_idx + 1),
        )
        for start_idx, end_idx in runs
    ]


def audit_weighted(weighted_df: pd.DataFrame) -> dict:
    first_year = weighted_df.loc[weighted_df["all_active_devices_first_year"]].copy()
    first_year_weight_mismatches = (
        first_year["sum_weights"].sub(first_year["n_active_devices"]).abs().gt(1e-9).sum()
    )
    increases = weighted_df["eta_weighted_avg"].diff().gt(1e-9)
    runs = sustained_increase_runs(weighted_df)
    return {
        "rows": int(len(weighted_df)),
        "min_month": weighted_df["month"].min().date().isoformat(),
        "max_month": weighted_df["month"].max().date().isoformat(),
        "missing_eta_weighted_avg_months": int(weighted_df["eta_weighted_avg"].isna().sum()),
        "zero_active_device_months": int(weighted_df["n_active_devices"].eq(0).sum()),
        "eta_weighted_avg_increase_months": int(increases.sum()),
        "sustained_increase_runs_3plus_months": int(len(runs)),
        "first_year_weight_mismatches": int(first_year_weight_mismatches),
        "min_active_devices": int(weighted_df["n_active_devices"].min()),
        "max_active_devices": int(weighted_df["n_active_devices"].max()),
        "final_eta_weighted_avg": float(weighted_df["eta_weighted_avg"].iloc[-1]),
    }


def write_audit_md(audit: dict, weighted_df: pd.DataFrame, output_path: Path) -> None:
    runs = sustained_increase_runs(weighted_df)
    lines = [
        "# Weighted-Average Hardware Efficiency Audit",
        "",
        "Source: `data/processed/hardware/hardware_master_clean.csv`",
        "",
        "Rules:",
        "",
        f"- Deployment month: release month plus `{DEPLOYMENT_LAG_MONTHS}` months",
        f"- Active device window: deployment month through month `{MAX_ACTIVE_MONTHS - 1}` after deployment",
        "- Weights: `1.0`, `0.8`, `0.6`, `0.4`, `0.2` for years 1 through 5 of active life",
        "- Weighted efficiency: sum of weighted `efficiency_j_per_th` divided by sum of weights",
        "",
    ]
    for key, value in audit.items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "## Sustained Increase Runs", ""])
    if not runs:
        lines.append("No sustained runs of three or more consecutive monthly increases were found.")
    else:
        lines.append("| start_month | end_month | length_months |")
        lines.append("|---|---|---|")
        for start, end, length in runs:
            lines.append(f"| {start} | {end} | {length} |")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    config = load_config()
    processed = processed_dir(config)
    backbone_path = processed / "backbone" / "backbone_monthly.csv"
    hardware_path = processed / "hardware" / "hardware_master_clean.csv"
    out = processed / "hardware"

    monthly_backbone = pd.read_csv(backbone_path)
    hardware = pd.read_csv(hardware_path)
    weighted_df = build_weighted_path(monthly_backbone, hardware)
    audit = audit_weighted(weighted_df)

    weighted_df.to_csv(out / "weighted_efficiency_monthly.csv", index=False)
    pd.DataFrame([audit]).to_csv(out / "weighted_efficiency_monthly_audit.csv", index=False)
    write_audit_md(audit, weighted_df, out / "weighted_efficiency_monthly_audit.md")

    print(f"Wrote weighted-average efficiency files to {out}")
    print("Created:")
    for file_name in [
        "weighted_efficiency_monthly.csv",
        "weighted_efficiency_monthly_audit.csv",
        "weighted_efficiency_monthly_audit.md",
    ]:
        print(f"- {out / file_name}")


if __name__ == "__main__":
    main()
