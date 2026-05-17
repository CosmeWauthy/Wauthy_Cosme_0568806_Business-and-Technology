from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / ".matplotlib-cache"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from statsmodels.tsa.stattools import adfuller, kpss


ANALYSIS_START_MONTH = pd.Timestamp("2010-08-01")
ANALYSIS_END_MONTH = pd.Timestamp("2025-12-01")
CORE_LOG_VARIABLES = [
    "log_bitcoin_market_price_usd",
    "log_mci_weighted",
    "log_mci_frontier",
]
VARIABLE_LABELS = {
    "log_bitcoin_market_price_usd": "Log Bitcoin market price",
    "log_mci_weighted": "Log MCI, weighted efficiency",
    "log_mci_frontier": "Log MCI, frontier efficiency",
}


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "config" / "paths.yaml"
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def read_analysis_panel(processed: Path) -> pd.DataFrame:
    panel = pd.read_csv(processed / "monthly" / "monthly_master_panel.csv")
    panel["month"] = pd.to_datetime(panel["month"])
    analysis = panel.loc[
        panel["month"].between(ANALYSIS_START_MONTH, ANALYSIS_END_MONTH),
        ["month", *CORE_LOG_VARIABLES],
    ].copy()
    analysis = analysis.sort_values("month").reset_index(drop=True)

    expected_months = pd.date_range(ANALYSIS_START_MONTH, ANALYSIS_END_MONTH, freq="MS")
    missing_months = expected_months.difference(analysis["month"])
    if len(missing_months) > 0:
        missing = ", ".join(month.date().isoformat() for month in missing_months)
        raise ValueError(f"Analysis sample has missing monthly observations: {missing}")
    if analysis["month"].duplicated().any():
        duplicates = analysis.loc[analysis["month"].duplicated(), "month"]
        duplicate_text = ", ".join(month.date().isoformat() for month in duplicates)
        raise ValueError(f"Analysis sample has duplicate months: {duplicate_text}")
    if analysis[CORE_LOG_VARIABLES].isna().any().any():
        missing_counts = analysis[CORE_LOG_VARIABLES].isna().sum()
        raise ValueError(f"Core log variables contain missing values:\n{missing_counts}")
    if not np.isfinite(analysis[CORE_LOG_VARIABLES].to_numpy()).all():
        raise ValueError("Core log variables contain nonfinite values.")

    return analysis


def descriptive_summary(analysis: pd.DataFrame) -> pd.DataFrame:
    levels = analysis[CORE_LOG_VARIABLES].copy()
    diffs = levels.diff().dropna().rename(columns={col: f"d_{col}" for col in CORE_LOG_VARIABLES})

    rows: list[dict] = []
    for transformation, frame in [("level", levels), ("first_difference", diffs)]:
        for col in frame.columns:
            base_col = col.removeprefix("d_")
            series = frame[col].dropna()
            rows.append(
                {
                    "variable": base_col,
                    "label": VARIABLE_LABELS[base_col],
                    "transformation": transformation,
                    "n": int(series.size),
                    "mean": float(series.mean()),
                    "std": float(series.std(ddof=1)),
                    "min": float(series.min()),
                    "p25": float(series.quantile(0.25)),
                    "median": float(series.median()),
                    "p75": float(series.quantile(0.75)),
                    "max": float(series.max()),
                }
            )
    return pd.DataFrame(rows)


def run_adf(series: pd.Series, regression: str) -> dict:
    result = adfuller(series.dropna(), regression=regression, autolag="AIC")
    return {
        "test": "ADF",
        "deterministic": regression,
        "statistic": float(result[0]),
        "p_value": float(result[1]),
        "lags_used": int(result[2]),
        "nobs": int(result[3]),
        "critical_1pct": float(result[4]["1%"]),
        "critical_5pct": float(result[4]["5%"]),
        "critical_10pct": float(result[4]["10%"]),
    }


def run_kpss(series: pd.Series, regression: str) -> dict:
    statistic, p_value, lags, critical = kpss(series.dropna(), regression=regression, nlags="auto")
    return {
        "test": "KPSS",
        "deterministic": regression,
        "statistic": float(statistic),
        "p_value": float(p_value),
        "lags_used": int(lags),
        "nobs": int(series.dropna().size),
        "critical_1pct": float(critical["1%"]),
        "critical_5pct": float(critical["5%"]),
        "critical_10pct": float(critical["10%"]),
    }


def stationarity_tests(analysis: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for variable in CORE_LOG_VARIABLES:
        level = analysis[variable]
        first_difference = level.diff().dropna()
        for transformation, series in [("level", level), ("first_difference", first_difference)]:
            specs = [
                ("ADF", "c"),
                ("ADF", "ct"),
                ("KPSS", "c"),
                ("KPSS", "ct"),
            ]
            for test, deterministic in specs:
                result = (
                    run_adf(series, deterministic)
                    if test == "ADF"
                    else run_kpss(series, deterministic)
                )
                result.update(
                    {
                        "variable": variable,
                        "label": VARIABLE_LABELS[variable],
                        "transformation": transformation,
                        "reject_at_5pct": bool(
                            result["p_value"] < 0.05
                            if test == "ADF"
                            else result["statistic"] > result["critical_5pct"]
                        ),
                    }
                )
                rows.append(result)
    cols = [
        "variable",
        "label",
        "transformation",
        "test",
        "deterministic",
        "statistic",
        "p_value",
        "lags_used",
        "nobs",
        "critical_1pct",
        "critical_5pct",
        "critical_10pct",
        "reject_at_5pct",
    ]
    return pd.DataFrame(rows)[cols]


def integration_conclusions(tests: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for variable in CORE_LOG_VARIABLES:
        subset = tests.loc[tests["variable"].eq(variable)]
        level = subset.loc[subset["transformation"].eq("level")]
        diff = subset.loc[subset["transformation"].eq("first_difference")]

        level_adf_rejects = int(level.loc[level["test"].eq("ADF"), "reject_at_5pct"].sum())
        level_kpss_rejects = int(level.loc[level["test"].eq("KPSS"), "reject_at_5pct"].sum())
        diff_adf_rejects = int(diff.loc[diff["test"].eq("ADF"), "reject_at_5pct"].sum())
        diff_kpss_rejects = int(diff.loc[diff["test"].eq("KPSS"), "reject_at_5pct"].sum())

        plausible_i1 = (
            level_adf_rejects == 0
            and level_kpss_rejects >= 1
            and diff_adf_rejects >= 1
            and diff_kpss_rejects == 0
        )
        rows.append(
            {
                "variable": variable,
                "label": VARIABLE_LABELS[variable],
                "level_adf_rejects_5pct": level_adf_rejects,
                "level_kpss_rejects_5pct": level_kpss_rejects,
                "diff_adf_rejects_5pct": diff_adf_rejects,
                "diff_kpss_rejects_5pct": diff_kpss_rejects,
                "plausibly_i1": plausible_i1,
                "conclusion": "Plausibly I(1)" if plausible_i1 else "Ambiguous, inspect before Johansen",
            }
        )
    return pd.DataFrame(rows)


def plot_levels_and_differences(analysis: pd.DataFrame, output_path: Path) -> None:
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(13, 9), sharex="col")
    for row_idx, variable in enumerate(CORE_LOG_VARIABLES):
        label = VARIABLE_LABELS[variable]
        axes[row_idx, 0].plot(analysis["month"], analysis[variable], color="#245c8a", linewidth=1.5)
        axes[row_idx, 0].set_title(f"{label}: level")
        axes[row_idx, 0].grid(alpha=0.25)

        diff = analysis[variable].diff()
        axes[row_idx, 1].plot(analysis["month"], diff, color="#8a4f24", linewidth=1.2)
        axes[row_idx, 1].axhline(0, color="#444444", linewidth=0.8)
        axes[row_idx, 1].set_title(f"{label}: first difference")
        axes[row_idx, 1].grid(alpha=0.25)

    fig.suptitle("Preliminary Diagnostics: Levels and First Differences", y=0.995)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def write_markdown(
    summary: dict,
    descriptives: pd.DataFrame,
    tests: pd.DataFrame,
    conclusions: pd.DataFrame,
    output_path: Path,
) -> None:
    lines = [
        "# Preliminary Stationarity Diagnostics",
        "",
        f"- Analysis sample: `{summary['analysis_min_month']}` to `{summary['analysis_max_month']}`",
        f"- Monthly observations: `{summary['analysis_rows']}`",
        f"- Duplicate months: `{summary['duplicate_months']}`",
        f"- Missing months inside analysis span: `{summary['missing_months_inside_span']}`",
        "",
        "## Integration Summary",
        "",
        conclusions.to_markdown(index=False),
        "",
        "## Descriptive Summary",
        "",
        descriptives.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## ADF and KPSS Results",
        "",
        tests.to_markdown(index=False, floatfmt=".4f"),
        "",
        "Notes:",
        "",
        "- ADF null: unit root. Rejection supports stationarity under the stated deterministic specification.",
        "- KPSS null: stationarity around the stated deterministic specification. Rejection supports nonstationarity.",
        "- `c` means constant only; `ct` means constant plus linear trend.",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    config = load_config()
    paths = config["paths"]
    processed = Path(paths["processed_data"])
    tables = Path(paths["tables"])
    figures = Path(paths["figures"])
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    analysis = read_analysis_panel(processed)
    expected_months = pd.date_range(ANALYSIS_START_MONTH, ANALYSIS_END_MONTH, freq="MS")
    summary = {
        "analysis_rows": int(len(analysis)),
        "analysis_min_month": analysis["month"].min().date().isoformat(),
        "analysis_max_month": analysis["month"].max().date().isoformat(),
        "duplicate_months": int(analysis["month"].duplicated().sum()),
        "missing_months_inside_span": int(len(expected_months.difference(analysis["month"]))),
    }

    descriptives = descriptive_summary(analysis)
    tests = stationarity_tests(analysis)
    conclusions = integration_conclusions(tests)

    analysis_with_diffs = analysis.copy()
    for variable in CORE_LOG_VARIABLES:
        analysis_with_diffs[f"d_{variable}"] = analysis_with_diffs[variable].diff()

    analysis_with_diffs.to_csv(tables / "preliminary_diagnostics_series.csv", index=False)
    descriptives.to_csv(tables / "preliminary_diagnostics_descriptives.csv", index=False)
    tests.to_csv(tables / "stationarity_adf_kpss_results.csv", index=False)
    conclusions.to_csv(tables / "stationarity_integration_summary.csv", index=False)
    plot_levels_and_differences(analysis, figures / "preliminary_diagnostics_levels_diffs.png")
    write_markdown(
        summary,
        descriptives,
        tests,
        conclusions,
        tables / "preliminary_stationarity_diagnostics.md",
    )

    print("Preliminary diagnostics complete.")
    print(f"Analysis sample: {summary['analysis_min_month']} to {summary['analysis_max_month']}")
    print(f"Rows: {summary['analysis_rows']}")
    print("Created:")
    for path in [
        tables / "preliminary_diagnostics_series.csv",
        tables / "preliminary_diagnostics_descriptives.csv",
        tables / "stationarity_adf_kpss_results.csv",
        tables / "stationarity_integration_summary.csv",
        tables / "preliminary_stationarity_diagnostics.md",
        figures / "preliminary_diagnostics_levels_diffs.png",
    ]:
        print(f"- {path}")


if __name__ == "__main__":
    main()
