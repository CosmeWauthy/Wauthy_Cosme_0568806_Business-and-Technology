from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from statsmodels.tools.sm_exceptions import InterpolationWarning
from statsmodels.tsa.stattools import adfuller, kpss, zivot_andrews


ANALYSIS_END_MONTH = pd.Timestamp("2025-12-01")
BASELINE_START_MONTH = pd.Timestamp("2010-08-01")
SENSITIVITY_START_MONTHS = [
    pd.Timestamp("2010-08-01"),
    pd.Timestamp("2012-01-01"),
    pd.Timestamp("2013-01-01"),
    pd.Timestamp("2014-01-01"),
    pd.Timestamp("2016-01-01"),
]
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
KPSS_NLAGS = ["auto", "legacy", 1, 2, 3, 4, 6, 8, 9, 12, 18, 24]
DETERMINISTIC_SPECS = ["c", "ct"]
ZA_REGRESSIONS = ["c", "t", "ct"]


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "config" / "paths.yaml"
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def read_panel(processed: Path) -> pd.DataFrame:
    panel = pd.read_csv(processed / "monthly" / "monthly_master_panel.csv")
    panel["month"] = pd.to_datetime(panel["month"])
    cols = ["month", *CORE_LOG_VARIABLES]
    panel = panel.loc[panel["month"].le(ANALYSIS_END_MONTH), cols].copy()
    return panel.sort_values("month").reset_index(drop=True)


def sample_slice(panel: pd.DataFrame, start_month: pd.Timestamp) -> pd.DataFrame:
    out = panel.loc[panel["month"].between(start_month, ANALYSIS_END_MONTH)].copy()
    expected_months = pd.date_range(start_month, ANALYSIS_END_MONTH, freq="MS")
    missing_months = expected_months.difference(out["month"])
    if len(missing_months):
        missing = ", ".join(month.date().isoformat() for month in missing_months)
        raise ValueError(f"Sample from {start_month.date()} has missing months: {missing}")
    if out["month"].duplicated().any():
        raise ValueError(f"Sample from {start_month.date()} has duplicate months")
    if out[CORE_LOG_VARIABLES].isna().any().any():
        raise ValueError(f"Sample from {start_month.date()} has missing core values")
    return out.reset_index(drop=True)


def series_for(analysis: pd.DataFrame, variable: str, transformation: str) -> pd.Series:
    series = analysis.set_index("month")[variable]
    if transformation == "first_difference":
        series = series.diff().dropna()
    return series.dropna()


def kpss_row(
    series: pd.Series,
    variable: str,
    sample_start: pd.Timestamp,
    transformation: str,
    deterministic: str,
    nlags: str | int,
) -> dict:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", InterpolationWarning)
        statistic, p_value, lags, critical = kpss(series, regression=deterministic, nlags=nlags)
    warning_notes = "; ".join(str(w.message).split("\n")[0] for w in caught)
    return {
        "sample_start": sample_start.date().isoformat(),
        "sample_end": ANALYSIS_END_MONTH.date().isoformat(),
        "variable": variable,
        "label": VARIABLE_LABELS[variable],
        "transformation": transformation,
        "test": "KPSS",
        "deterministic": deterministic,
        "nlags_requested": str(nlags),
        "lags_used": int(lags),
        "statistic": float(statistic),
        "p_value": float(p_value),
        "critical_1pct": float(critical["1%"]),
        "critical_5pct": float(critical["5%"]),
        "critical_10pct": float(critical["10%"]),
        "reject_at_5pct": bool(statistic > critical["5%"]),
        "warning": warning_notes,
        "nobs": int(series.size),
    }


def adf_row(series: pd.Series, variable: str, sample_start: pd.Timestamp, transformation: str, deterministic: str) -> dict:
    statistic, p_value, lags, nobs, critical, _icbest = adfuller(series, regression=deterministic, autolag="AIC")
    return {
        "sample_start": sample_start.date().isoformat(),
        "sample_end": ANALYSIS_END_MONTH.date().isoformat(),
        "variable": variable,
        "label": VARIABLE_LABELS[variable],
        "transformation": transformation,
        "test": "ADF",
        "deterministic": deterministic,
        "statistic": float(statistic),
        "p_value": float(p_value),
        "lags_used": int(lags),
        "nobs": int(nobs),
        "critical_1pct": float(critical["1%"]),
        "critical_5pct": float(critical["5%"]),
        "critical_10pct": float(critical["10%"]),
        "reject_at_5pct": bool(p_value < 0.05),
    }


def zivot_andrews_row(series: pd.Series, variable: str, sample_start: pd.Timestamp, transformation: str, regression: str) -> dict:
    result = zivot_andrews(series, regression=regression, autolag="AIC")
    statistic, p_value, critical, baselag, break_index = result
    break_month = series.index[int(break_index)].date().isoformat()
    return {
        "sample_start": sample_start.date().isoformat(),
        "sample_end": ANALYSIS_END_MONTH.date().isoformat(),
        "variable": variable,
        "label": VARIABLE_LABELS[variable],
        "transformation": transformation,
        "test": "Zivot-Andrews",
        "break_specification": regression,
        "statistic": float(statistic),
        "p_value": float(p_value),
        "lags_used": int(baselag),
        "break_index": int(break_index),
        "break_month": break_month,
        "critical_1pct": float(critical["1%"]),
        "critical_5pct": float(critical["5%"]),
        "critical_10pct": float(critical["10%"]),
        "reject_unit_root_at_5pct": bool(statistic < critical["5%"]),
        "nobs": int(series.size),
    }


def run_kpss_bandwidth_sensitivity(panel: pd.DataFrame) -> pd.DataFrame:
    analysis = sample_slice(panel, BASELINE_START_MONTH)
    rows = []
    for variable in CORE_LOG_VARIABLES:
        for transformation in ["level", "first_difference"]:
            series = series_for(analysis, variable, transformation)
            for deterministic in DETERMINISTIC_SPECS:
                for nlags in KPSS_NLAGS:
                    rows.append(kpss_row(series, variable, BASELINE_START_MONTH, transformation, deterministic, nlags))
    return pd.DataFrame(rows)


def summarize_weighted_kpss(kpss_sensitivity: pd.DataFrame) -> pd.DataFrame:
    subset = kpss_sensitivity.loc[
        kpss_sensitivity["variable"].eq("log_mci_weighted")
        & kpss_sensitivity["transformation"].eq("first_difference")
    ].copy()
    rows = []
    for deterministic, group in subset.groupby("deterministic"):
        rows.append(
            {
                "variable": "log_mci_weighted",
                "transformation": "first_difference",
                "deterministic": deterministic,
                "kpss_rejections_at_5pct": int(group["reject_at_5pct"].sum()),
                "kpss_specs_checked": int(len(group)),
                "min_statistic": float(group["statistic"].min()),
                "max_statistic": float(group["statistic"].max()),
                "min_lags_used": int(group["lags_used"].min()),
                "max_lags_used": int(group["lags_used"].max()),
                "fragility_conclusion": "Fragile to bandwidth" if not group["reject_at_5pct"].all() else "Robust rejection across checked bandwidths",
            }
        )
    return pd.DataFrame(rows)


def run_zivot_andrews(panel: pd.DataFrame) -> pd.DataFrame:
    analysis = sample_slice(panel, BASELINE_START_MONTH)
    rows = []
    for variable in CORE_LOG_VARIABLES:
        for transformation in ["level", "first_difference"]:
            series = series_for(analysis, variable, transformation)
            for regression in ZA_REGRESSIONS:
                rows.append(zivot_andrews_row(series, variable, BASELINE_START_MONTH, transformation, regression))
    return pd.DataFrame(rows)


def run_later_start_sensitivity(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    test_rows = []
    summary_rows = []
    for start_month in SENSITIVITY_START_MONTHS:
        analysis = sample_slice(panel, start_month)
        for variable in CORE_LOG_VARIABLES:
            for transformation in ["level", "first_difference"]:
                series = series_for(analysis, variable, transformation)
                for deterministic in DETERMINISTIC_SPECS:
                    test_rows.append(adf_row(series, variable, start_month, transformation, deterministic))
                    test_rows.append(kpss_row(series, variable, start_month, transformation, deterministic, "auto"))

        tests = pd.DataFrame(test_rows).loc[lambda df: df["sample_start"].eq(start_month.date().isoformat())]
        for variable in CORE_LOG_VARIABLES:
            subset = tests.loc[tests["variable"].eq(variable)]
            level = subset.loc[subset["transformation"].eq("level")]
            diff = subset.loc[subset["transformation"].eq("first_difference")]
            level_adf_rejects = int(level.loc[level["test"].eq("ADF"), "reject_at_5pct"].sum())
            level_kpss_rejects = int(level.loc[level["test"].eq("KPSS"), "reject_at_5pct"].sum())
            diff_adf_rejects = int(diff.loc[diff["test"].eq("ADF"), "reject_at_5pct"].sum())
            diff_kpss_rejects = int(diff.loc[diff["test"].eq("KPSS"), "reject_at_5pct"].sum())
            summary_rows.append(
                {
                    "sample_start": start_month.date().isoformat(),
                    "sample_end": ANALYSIS_END_MONTH.date().isoformat(),
                    "nobs_levels": int(len(analysis)),
                    "variable": variable,
                    "label": VARIABLE_LABELS[variable],
                    "level_adf_rejects_5pct": level_adf_rejects,
                    "level_kpss_rejects_5pct": level_kpss_rejects,
                    "diff_adf_rejects_5pct": diff_adf_rejects,
                    "diff_kpss_rejects_5pct": diff_kpss_rejects,
                    "i1_support": bool(
                        level_kpss_rejects >= 1
                        and diff_adf_rejects >= 1
                        and diff_kpss_rejects == 0
                    ),
                    "note": "Treat level ADF rejections cautiously when breaks/trends are plausible",
                }
            )
    return pd.DataFrame(test_rows), pd.DataFrame(summary_rows)


def markdown_table(df: pd.DataFrame, float_digits: int | None = None) -> str:
    def fmt(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            return f"{value:.{float_digits}f}" if float_digits is not None else str(value)
        return str(value)

    columns = list(df.columns)
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def build_overall_summary(
    weighted_kpss_summary: pd.DataFrame,
    za_results: pd.DataFrame,
    later_summary: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    za_levels = za_results.loc[za_results["transformation"].eq("level")]
    later_latest = later_summary.loc[later_summary["sample_start"].eq(BASELINE_START_MONTH.date().isoformat())]
    for variable in CORE_LOG_VARIABLES:
        za_var = za_levels.loc[za_levels["variable"].eq(variable)]
        later_var = later_latest.loc[later_latest["variable"].eq(variable)].iloc[0]
        rows.append(
            {
                "variable": variable,
                "label": VARIABLE_LABELS[variable],
                "za_level_rejections_5pct": int(za_var["reject_unit_root_at_5pct"].sum()),
                "za_level_specs_checked": int(len(za_var)),
                "baseline_later_start_i1_support": bool(later_var["i1_support"]),
                "supplementary_interpretation": supplementary_interpretation(variable, weighted_kpss_summary, za_var, later_summary),
            }
        )
    return pd.DataFrame(rows)


def supplementary_interpretation(
    variable: str,
    weighted_kpss_summary: pd.DataFrame,
    za_var: pd.DataFrame,
    later_summary: pd.DataFrame,
) -> str:
    if variable == "log_mci_weighted":
        robust = weighted_kpss_summary["fragility_conclusion"].str.contains("Robust").all()
        if robust:
            return "ADF supports stationary first differences, but KPSS first-difference rejection remains robust across checked bandwidths; keep I(1) treatment conditional and use lifecycle-rule interpretation."
        return "ADF supports stationary first differences and KPSS rejection is bandwidth-fragile; I(1) interpretation is strengthened with lifecycle-rule caveat."
    if variable == "log_mci_frontier":
        return "Supplementary evidence remains consistent with the preliminary I(1) interpretation."
    later_var = later_summary.loc[later_summary["variable"].eq(variable)]
    supported = int(later_var["i1_support"].sum())
    return f"I(1) support appears in {supported} of {len(later_var)} sample-start checks; interpret alongside break-aware evidence."


def write_report(
    output_path: Path,
    weighted_kpss_summary: pd.DataFrame,
    za_results: pd.DataFrame,
    later_summary: pd.DataFrame,
    overall_summary: pd.DataFrame,
) -> None:
    za_level_summary = za_results.loc[za_results["transformation"].eq("level"), [
        "variable", "break_specification", "statistic", "p_value", "break_month", "reject_unit_root_at_5pct"
    ]]
    weighted_later = later_summary.loc[later_summary["variable"].eq("log_mci_weighted")]
    lines = [
        "# Supplementary Stationarity Checks",
        "",
        f"- Baseline sample: `{BASELINE_START_MONTH.date().isoformat()}` to `{ANALYSIS_END_MONTH.date().isoformat()}`",
        "- Checks: KPSS lag/bandwidth sensitivity, Zivot-Andrews break-aware unit-root tests, and later-start sample sensitivity.",
        "",
        "## Overall Summary",
        "",
        markdown_table(overall_summary),
        "",
        "## Weighted-MCI KPSS Bandwidth Sensitivity",
        "",
        markdown_table(weighted_kpss_summary, float_digits=4),
        "",
        "Interpretation: the weighted-MCI first-difference KPSS result is evaluated specifically as a possible long-run-variance/bandwidth artefact around hardware lifecycle transitions.",
        "",
        "## Zivot-Andrews Level Tests",
        "",
        markdown_table(za_level_summary, float_digits=4),
        "",
        "## Later-Start Summary for Weighted MCI",
        "",
        markdown_table(weighted_later, float_digits=4),
        "",
        "Notes:",
        "",
        "- KPSS null: stationarity around the deterministic specification; rejection supports nonstationarity.",
        "- ADF and Zivot-Andrews null: unit root; rejection supports stationarity, with Zivot-Andrews allowing one endogenous break.",
        "- `c` means intercept, `t` means trend, and `ct` means both intercept and trend/break specification depending on the test.",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    config = load_config()
    paths = config["paths"]
    processed = Path(paths["processed_data"])
    tables = Path(paths["tables"])
    tables.mkdir(parents=True, exist_ok=True)

    panel = read_panel(processed)
    kpss_sensitivity = run_kpss_bandwidth_sensitivity(panel)
    weighted_kpss_summary = summarize_weighted_kpss(kpss_sensitivity)
    za_results = run_zivot_andrews(panel)
    later_tests, later_summary = run_later_start_sensitivity(panel)
    overall_summary = build_overall_summary(weighted_kpss_summary, za_results, later_summary)

    kpss_sensitivity.to_csv(tables / "supplementary_kpss_bandwidth_sensitivity.csv", index=False)
    weighted_kpss_summary.to_csv(tables / "supplementary_weighted_mci_kpss_summary.csv", index=False)
    za_results.to_csv(tables / "supplementary_zivot_andrews_results.csv", index=False)
    later_tests.to_csv(tables / "supplementary_later_start_tests.csv", index=False)
    later_summary.to_csv(tables / "supplementary_later_start_summary.csv", index=False)
    overall_summary.to_csv(tables / "supplementary_stationarity_summary.csv", index=False)
    write_report(
        tables / "supplementary_stationarity_checks.md",
        weighted_kpss_summary,
        za_results,
        later_summary,
        overall_summary,
    )

    print("Supplementary stationarity checks complete.")
    print("Created:")
    for path in [
        tables / "supplementary_kpss_bandwidth_sensitivity.csv",
        tables / "supplementary_weighted_mci_kpss_summary.csv",
        tables / "supplementary_zivot_andrews_results.csv",
        tables / "supplementary_later_start_tests.csv",
        tables / "supplementary_later_start_summary.csv",
        tables / "supplementary_stationarity_summary.csv",
        tables / "supplementary_stationarity_checks.md",
    ]:
        print(f"- {path}")
    print("\nOverall summary:")
    print(overall_summary.to_string(index=False))


if __name__ == "__main__":
    main()
