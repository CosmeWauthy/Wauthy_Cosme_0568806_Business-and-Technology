from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


CUTOFF_DATE = pd.Timestamp("2025-12-31")
ASIC_FILL_START = pd.Timestamp("2014-01-01")


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "config" / "paths.yaml"
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def raw_dir(config: dict) -> Path:
    return Path(config["paths"]["raw_data"])


def output_dir(config: dict) -> Path:
    path = Path(config["paths"]["processed_data"]) / "hardware"
    path.mkdir(parents=True, exist_ok=True)
    return path


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype("string").str.replace(",", "", regex=False).str.strip(),
        errors="coerce",
    )


def clean_hardware(base: Path) -> pd.DataFrame:
    path = base / "Mining equipment list - list.csv"
    df = pd.read_csv(path, skiprows=3)
    df.columns = [col.strip().replace("\n", " ") for col in df.columns]

    df = df.rename(
        columns={
            "Miner_name": "hardware_model",
            "Type": "hardware_type",
            "Date of release": "release_date",
            "UNIX_date_of_release": "release_timestamp_unix",
            "Hashing power (Th/s)": "hashrate_th_s",
            "Power (W)": "power_w",
            "Efficiency (J/Gh)": "efficiency_j_per_gh",
            "Weight in kg": "weight_kg",
            "Efficiency: suggested alternative(s)": "efficiency_suggested_alternatives",
            "Included in  version": "included_in_version",
            "Additional comments": "additional_comments",
        }
    )

    df["hardware_model"] = df["hardware_model"].astype("string").str.strip()
    df["hardware_type"] = df["hardware_type"].astype("string").str.strip()
    df.loc[df["hardware_type"].isin(["", "nan", "NaN"]), "hardware_type"] = pd.NA
    df["release_date"] = pd.to_datetime(df["release_date"], dayfirst=True, errors="coerce")

    numeric_cols = [
        "release_timestamp_unix",
        "hashrate_th_s",
        "power_w",
        "efficiency_j_per_gh",
        "weight_kg",
    ]
    for col in numeric_cols:
        df[col] = to_numeric(df[col])

    post_2013_missing_type = df["hardware_type"].isna() & df["release_date"].ge(ASIC_FILL_START)
    df["hardware_type_filled_post_2013_as_asic"] = post_2013_missing_type
    df.loc[post_2013_missing_type, "hardware_type"] = "ASIC"

    df["efficiency_j_per_th"] = df["efficiency_j_per_gh"] * 1000
    df = df.loc[df["release_date"].le(CUTOFF_DATE)].copy()
    df = df.sort_values(["release_date", "hardware_model"]).reset_index(drop=True)

    output_cols = [
        "hardware_model",
        "hardware_type",
        "release_date",
        "release_timestamp_unix",
        "hashrate_th_s",
        "power_w",
        "efficiency_j_per_gh",
        "efficiency_j_per_th",
        "weight_kg",
        "efficiency_suggested_alternatives",
        "included_in_version",
        "additional_comments",
        "hardware_type_filled_post_2013_as_asic",
    ]
    return df.loc[:, output_cols]


def audit_hardware(df: pd.DataFrame, raw_rows: int) -> dict:
    return {
        "raw_rows": int(raw_rows),
        "clean_rows_after_cutoff": int(len(df)),
        "cutoff_date": CUTOFF_DATE.date().isoformat(),
        "min_release_date": df["release_date"].min().date().isoformat(),
        "max_release_date": df["release_date"].max().date().isoformat(),
        "missing_hardware_model": int(df["hardware_model"].isna().sum()),
        "missing_hardware_type": int(df["hardware_type"].isna().sum()),
        "missing_release_date": int(df["release_date"].isna().sum()),
        "missing_hashrate_th_s": int(df["hashrate_th_s"].isna().sum()),
        "missing_power_w": int(df["power_w"].isna().sum()),
        "missing_efficiency_j_per_th": int(df["efficiency_j_per_th"].isna().sum()),
        "post_2013_types_filled_as_asic": int(df["hardware_type_filled_post_2013_as_asic"].sum()),
    }


def write_audit_md(audit: dict, output_path: Path) -> None:
    lines = [
        "# Hardware Cleaning Audit",
        "",
        "Source: `Mining equipment list - list.csv`",
        "",
        "Rule: missing `Type` values are filled as `ASIC` for models released on or after `2014-01-01`.",
        "",
    ]
    for key, value in audit.items():
        lines.append(f"- `{key}`: {value}")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    config = load_config()
    raw = raw_dir(config)
    out = output_dir(config)

    source = pd.read_csv(raw / "Mining equipment list - list.csv", skiprows=3)
    hardware_df = clean_hardware(raw)
    audit = audit_hardware(hardware_df, len(source))

    hardware_df.to_csv(out / "hardware_master_clean.csv", index=False)
    pd.DataFrame([audit]).to_csv(out / "hardware_master_audit.csv", index=False)
    write_audit_md(audit, out / "hardware_master_audit.md")

    print(f"Wrote cleaned hardware files to {out}")
    print("Created:")
    for file_name in [
        "hardware_master_clean.csv",
        "hardware_master_audit.csv",
        "hardware_master_audit.md",
    ]:
        print(f"- {out / file_name}")


if __name__ == "__main__":
    main()
