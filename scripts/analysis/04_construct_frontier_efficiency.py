from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "config" / "paths.yaml"
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def processed_dir(config: dict) -> Path:
    return Path(config["paths"]["processed_data"])


def month_start(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.to_period("M").dt.to_timestamp()


def build_frontier_path(monthly_backbone: pd.DataFrame, hardware: pd.DataFrame) -> pd.DataFrame:
    months = pd.DataFrame({"month": pd.to_datetime(monthly_backbone["month"])})
    months = months.sort_values("month").reset_index(drop=True)

    hw = hardware.copy()
    hw["release_date"] = pd.to_datetime(hw["release_date"])
    hw["release_month"] = month_start(hw["release_date"])
    hw = hw.dropna(subset=["release_month", "efficiency_j_per_th"])
    hw = hw.sort_values(["release_month", "efficiency_j_per_th", "hardware_model"]).reset_index(drop=True)

    rows: list[dict] = []
    for month in months["month"]:
        available = hw.loc[hw["release_month"].le(month)]
        if available.empty:
            rows.append(
                {
                    "month": month,
                    "frontier_efficiency_j_per_th": pd.NA,
                    "frontier_hardware_model": pd.NA,
                    "frontier_hardware_type": pd.NA,
                    "frontier_release_date": pd.NaT,
                }
            )
            continue

        frontier = available.sort_values(
            ["efficiency_j_per_th", "release_date", "hardware_model"]
        ).iloc[0]
        rows.append(
            {
                "month": month,
                "frontier_efficiency_j_per_th": frontier["efficiency_j_per_th"],
                "frontier_hardware_model": frontier["hardware_model"],
                "frontier_hardware_type": frontier["hardware_type"],
                "frontier_release_date": frontier["release_date"],
            }
        )

    frontier_df = pd.DataFrame(rows)
    frontier_df["frontier_changed"] = (
        frontier_df["frontier_hardware_model"] != frontier_df["frontier_hardware_model"].shift(1)
    )
    frontier_df.loc[frontier_df["frontier_hardware_model"].isna(), "frontier_changed"] = False
    return frontier_df


def audit_frontier(frontier_df: pd.DataFrame) -> dict:
    efficiency = pd.to_numeric(frontier_df["frontier_efficiency_j_per_th"], errors="coerce")
    increases = efficiency.diff().gt(1e-9)
    return {
        "rows": int(len(frontier_df)),
        "min_month": frontier_df["month"].min().date().isoformat(),
        "max_month": frontier_df["month"].max().date().isoformat(),
        "missing_frontier_efficiency_months": int(efficiency.isna().sum()),
        "frontier_efficiency_increases": int(increases.sum()),
        "frontier_changes": int(frontier_df["frontier_changed"].sum()),
        "first_frontier_model": str(frontier_df.loc[frontier_df["frontier_changed"], "frontier_hardware_model"].iloc[0]),
        "last_frontier_model": str(frontier_df["frontier_hardware_model"].dropna().iloc[-1]),
        "last_frontier_efficiency_j_per_th": float(efficiency.dropna().iloc[-1]),
    }


def write_audit_md(audit: dict, frontier_df: pd.DataFrame, output_path: Path) -> None:
    changes = frontier_df.loc[
        frontier_df["frontier_changed"],
        [
            "month",
            "frontier_hardware_model",
            "frontier_hardware_type",
            "frontier_release_date",
            "frontier_efficiency_j_per_th",
        ],
    ].copy()

    lines = [
        "# Frontier Hardware Efficiency Audit",
        "",
        "Source: `data/processed/hardware/hardware_master_clean.csv`",
        "",
        "Rule: for each monthly backbone month, use the lowest `efficiency_j_per_th` among devices released in or before that calendar month.",
        "",
        "Interpretation: this is a lower-bound technology path, not a network-average operating-efficiency estimate.",
        "",
    ]
    for key, value in audit.items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "## Frontier Changes", ""])
    if changes.empty:
        lines.append("No frontier changes found.")
    else:
        table_cols = list(changes.columns)
        lines.append("| " + " | ".join(table_cols) + " |")
        lines.append("|" + "|".join(["---"] * len(table_cols)) + "|")
        for _, row in changes.iterrows():
            values = []
            for col in table_cols:
                value = row[col]
                if pd.isna(value):
                    values.append("")
                elif col in {"month", "frontier_release_date"}:
                    values.append(pd.to_datetime(value).date().isoformat())
                else:
                    values.append(str(value))
            lines.append("| " + " | ".join(values) + " |")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    config = load_config()
    processed = processed_dir(config)
    backbone_path = processed / "backbone" / "backbone_monthly.csv"
    hardware_path = processed / "hardware" / "hardware_master_clean.csv"
    out = processed / "hardware"

    monthly_backbone = pd.read_csv(backbone_path)
    hardware = pd.read_csv(hardware_path)
    frontier_df = build_frontier_path(monthly_backbone, hardware)
    audit = audit_frontier(frontier_df)

    frontier_df.to_csv(out / "frontier_efficiency_monthly.csv", index=False)
    pd.DataFrame([audit]).to_csv(out / "frontier_efficiency_monthly_audit.csv", index=False)
    write_audit_md(audit, frontier_df, out / "frontier_efficiency_monthly_audit.md")

    print(f"Wrote frontier efficiency files to {out}")
    print("Created:")
    for file_name in [
        "frontier_efficiency_monthly.csv",
        "frontier_efficiency_monthly_audit.csv",
        "frontier_efficiency_monthly_audit.md",
    ]:
        print(f"- {out / file_name}")


if __name__ == "__main__":
    main()
