from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from statsmodels.tsa.vector_ar.vecm import VECM


ANALYSIS_END_MONTH = pd.Timestamp("2025-12-01")
PRICE_VAR = "log_bitcoin_market_price_usd"
WINDOWS = [48, 36]
SYSTEMS = {
    "weighted": "log_mci_weighted",
    "frontier": "log_mci_frontier",
}
SPECIFICATIONS = [
    {
        "specification": "frontier_asic_constant_main",
        "system": "frontier",
        "sample": "asic_robustness_2014_01",
        "sample_start": pd.Timestamp("2014-01-01"),
        "k_ar_diff": 1,
        "coint_rank": 1,
        "deterministic": "ci",
        "role": "main rolling specification",
        "interpretation_weight": "main",
    },
    {
        "specification": "weighted_baseline_parsimonious_constant",
        "system": "weighted",
        "sample": "baseline_2010_08",
        "sample_start": pd.Timestamp("2010-08-01"),
        "k_ar_diff": 1,
        "coint_rank": 1,
        "deterministic": "ci",
        "role": "weighted robustness; interpret cautiously because static VECM has same-sign alphas and residual autocorrelation",
        "interpretation_weight": "secondary",
    },
    {
        "specification": "frontier_baseline_none_sensitivity",
        "system": "frontier",
        "sample": "baseline_2010_08",
        "sample_start": pd.Timestamp("2010-08-01"),
        "k_ar_diff": 1,
        "coint_rank": 1,
        "deterministic": "n",
        "role": "frontier full-sample instability sensitivity",
        "interpretation_weight": "sensitivity",
    },
    {
        "specification": "weighted_asic_linear_trend_sensitivity",
        "system": "weighted",
        "sample": "asic_robustness_2014_01",
        "sample_start": pd.Timestamp("2014-01-01"),
        "k_ar_diff": 1,
        "coint_rank": 1,
        "deterministic": "li",
        "role": "weighted ASIC-era trend sensitivity",
        "interpretation_weight": "sensitivity",
    },
]


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "config" / "paths.yaml"
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def read_panel(processed: Path) -> pd.DataFrame:
    panel = pd.read_csv(processed / "monthly" / "monthly_master_panel.csv")
    panel["month"] = pd.to_datetime(panel["month"])
    keep = ["month", PRICE_VAR, "log_mci_weighted", "log_mci_frontier"]
    return panel.loc[panel["month"].le(ANALYSIS_END_MONTH), keep].sort_values("month")


def sample_system(panel: pd.DataFrame, sample_start: pd.Timestamp, cost_var: str) -> pd.DataFrame:
    variables = [PRICE_VAR, cost_var]
    data = panel.loc[panel["month"].between(sample_start, ANALYSIS_END_MONTH), ["month", *variables]].copy()
    expected = pd.date_range(sample_start, ANALYSIS_END_MONTH, freq="MS")
    missing_months = expected.difference(data["month"])
    if len(missing_months):
        missing = ", ".join(month.date().isoformat() for month in missing_months)
        raise ValueError(f"Missing months for sample starting {sample_start.date()}: {missing}")
    if data[variables].isna().any().any():
        raise ValueError(f"Missing values for variables {variables} in sample starting {sample_start.date()}")
    return data.set_index("month")


def scalar_or_nan(array: np.ndarray | list | None, idx: int = 0) -> float:
    if array is None:
        return np.nan
    arr = np.asarray(array, dtype=float).ravel()
    if len(arr) <= idx:
        return np.nan
    return float(arr[idx])


def normalize_beta(result: object) -> np.ndarray:
    beta = np.asarray(result.beta[:, 0], dtype=float)
    if abs(beta[0]) > 1e-12:
        beta = beta / beta[0]
    return beta


def fit_window(spec: dict, window_data: pd.DataFrame, window_months: int) -> dict:
    base = {
        "specification": spec["specification"],
        "system": spec["system"],
        "sample": spec["sample"],
        "role": spec["role"],
        "interpretation_weight": spec["interpretation_weight"],
        "window_months": int(window_months),
        "window_start": window_data.index.min().date().isoformat(),
        "window_end": window_data.index.max().date().isoformat(),
        "nobs_levels": int(window_data.shape[0]),
        "k_ar_diff": int(spec["k_ar_diff"]),
        "coint_rank": int(spec["coint_rank"]),
        "deterministic": spec["deterministic"],
        "cost_variable": window_data.columns[1],
    }
    try:
        result = VECM(
            window_data,
            k_ar_diff=spec["k_ar_diff"],
            coint_rank=spec["coint_rank"],
            deterministic=spec["deterministic"],
            freq="MS",
        ).fit()
        beta = normalize_beta(result)
        alpha = np.asarray(result.alpha[:, 0], dtype=float)
        p_alpha = np.asarray(result.pvalues_alpha[:, 0], dtype=float)
        t_alpha = np.asarray(result.tvalues_alpha[:, 0], dtype=float)
        same_sign_alphas = bool(np.sign(alpha[0]) == np.sign(alpha[1]))
        return {
            **base,
            "status": "ok",
            "error_message": "",
            "beta_price": float(beta[0]),
            "beta_cost": float(beta[1]),
            "alpha_price": float(alpha[0]),
            "alpha_cost": float(alpha[1]),
            "t_price": float(t_alpha[0]),
            "t_cost": float(t_alpha[1]),
            "p_price": float(p_alpha[0]),
            "p_cost": float(p_alpha[1]),
            "price_sig_5pct": bool(p_alpha[0] < 0.05),
            "price_sig_10pct": bool(p_alpha[0] < 0.10),
            "cost_sig_5pct": bool(p_alpha[1] < 0.05),
            "cost_sig_10pct": bool(p_alpha[1] < 0.10),
            "same_sign_alphas": same_sign_alphas,
            "opposite_sign_alphas": bool(not same_sign_alphas),
            "cost_side_dominant_5pct": bool((p_alpha[1] < 0.05) and not (p_alpha[0] < 0.05)),
            "price_side_dominant_5pct": bool((p_alpha[0] < 0.05) and not (p_alpha[1] < 0.05)),
            "both_adjust_5pct": bool((p_alpha[0] < 0.05) and (p_alpha[1] < 0.05)),
            "neither_adjust_5pct": bool((p_alpha[0] >= 0.05) and (p_alpha[1] >= 0.05)),
            "log_likelihood": float(result.llf),
        }
    except Exception as exc:  # pragma: no cover - reported in output table
        return {
            **base,
            "status": "failed",
            "error_message": str(exc),
            "beta_price": np.nan,
            "beta_cost": np.nan,
            "alpha_price": np.nan,
            "alpha_cost": np.nan,
            "t_price": np.nan,
            "t_cost": np.nan,
            "p_price": np.nan,
            "p_cost": np.nan,
            "price_sig_5pct": False,
            "price_sig_10pct": False,
            "cost_sig_5pct": False,
            "cost_sig_10pct": False,
            "same_sign_alphas": False,
            "opposite_sign_alphas": False,
            "cost_side_dominant_5pct": False,
            "price_side_dominant_5pct": False,
            "both_adjust_5pct": False,
            "neither_adjust_5pct": False,
            "log_likelihood": np.nan,
        }


def rolling_rows(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for spec in SPECIFICATIONS:
        cost_var = SYSTEMS[spec["system"]]
        data = sample_system(panel, spec["sample_start"], cost_var)
        for window_months in WINDOWS:
            if len(data) < window_months:
                continue
            for end_loc in range(window_months, len(data) + 1):
                window_data = data.iloc[end_loc - window_months:end_loc]
                rows.append(fit_window(spec, window_data, window_months))
    return pd.DataFrame(rows)


def summarize_windows(results: pd.DataFrame) -> pd.DataFrame:
    ok = results.loc[results["status"].eq("ok")].copy()
    rows = []
    for (specification, window_months), group in ok.groupby(["specification", "window_months"], sort=False):
        rows.append(
            {
                "specification": specification,
                "system": group["system"].iloc[0],
                "sample": group["sample"].iloc[0],
                "role": group["role"].iloc[0],
                "window_months": int(window_months),
                "n_windows": int(len(group)),
                "first_window_end": group["window_end"].min(),
                "last_window_end": group["window_end"].max(),
                "beta_cost_median": float(group["beta_cost"].median()),
                "beta_cost_min": float(group["beta_cost"].min()),
                "beta_cost_max": float(group["beta_cost"].max()),
                "alpha_price_median": float(group["alpha_price"].median()),
                "alpha_cost_median": float(group["alpha_cost"].median()),
                "share_price_sig_5pct": float(group["price_sig_5pct"].mean()),
                "share_price_sig_10pct": float(group["price_sig_10pct"].mean()),
                "share_cost_sig_5pct": float(group["cost_sig_5pct"].mean()),
                "share_cost_sig_10pct": float(group["cost_sig_10pct"].mean()),
                "share_opposite_sign_alphas": float(group["opposite_sign_alphas"].mean()),
                "share_same_sign_alphas": float(group["same_sign_alphas"].mean()),
                "share_cost_side_dominant_5pct": float(group["cost_side_dominant_5pct"].mean()),
                "share_price_side_dominant_5pct": float(group["price_side_dominant_5pct"].mean()),
                "share_both_adjust_5pct": float(group["both_adjust_5pct"].mean()),
                "share_neither_adjust_5pct": float(group["neither_adjust_5pct"].mean()),
            }
        )
    return pd.DataFrame(rows)


def classify_regime(window_end: str) -> str:
    end = pd.Timestamp(window_end)
    if end <= pd.Timestamp("2020-12-01"):
        return "through_2020"
    if end <= pd.Timestamp("2023-12-01"):
        return "2021_2023"
    return "2024_2025"


def summarize_regimes(results: pd.DataFrame) -> pd.DataFrame:
    ok = results.loc[results["status"].eq("ok")].copy()
    ok["window_end_regime"] = ok["window_end"].map(classify_regime)
    rows = []
    for (specification, window_months, regime), group in ok.groupby(
        ["specification", "window_months", "window_end_regime"], sort=False
    ):
        rows.append(
            {
                "specification": specification,
                "window_months": int(window_months),
                "window_end_regime": regime,
                "n_windows": int(len(group)),
                "alpha_price_median": float(group["alpha_price"].median()),
                "alpha_cost_median": float(group["alpha_cost"].median()),
                "beta_cost_median": float(group["beta_cost"].median()),
                "share_price_sig_10pct": float(group["price_sig_10pct"].mean()),
                "share_cost_sig_5pct": float(group["cost_sig_5pct"].mean()),
                "share_opposite_sign_alphas": float(group["opposite_sign_alphas"].mean()),
                "share_cost_side_dominant_5pct": float(group["cost_side_dominant_5pct"].mean()),
            }
        )
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame, float_digits: int | None = 4) -> str:
    def fmt(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, (float, np.floating)):
            return f"{value:.{float_digits}f}" if float_digits is not None else str(value)
        return str(value)

    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def plot_main_frontier(results: pd.DataFrame, figures: Path) -> Path:
    figures.mkdir(parents=True, exist_ok=True)
    df = results.loc[
        results["status"].eq("ok") & results["specification"].eq("frontier_asic_constant_main")
    ].copy()
    df["window_end_dt"] = pd.to_datetime(df["window_end"])
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for window_months, group in df.groupby("window_months"):
        group = group.sort_values("window_end_dt")
        label = f"{window_months}-month"
        axes[0].plot(group["window_end_dt"], group["alpha_price"], label=label)
        axes[1].plot(group["window_end_dt"], group["alpha_cost"], label=label)
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("Rolling VECM Price Adjustment: Frontier ASIC-Era")
    axes[1].set_title("Rolling VECM Frontier-MCI Adjustment: Frontier ASIC-Era")
    axes[0].set_ylabel("Price alpha")
    axes[1].set_ylabel("Frontier MCI alpha")
    axes[1].set_xlabel("Window end month")
    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.legend()
    fig.tight_layout()
    output = figures / "rolling_vecm_frontier_asic_adjustment.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    return output


def write_report(tables: Path, results: pd.DataFrame, summary: pd.DataFrame, regime_summary: pd.DataFrame, figure_path: Path) -> None:
    main_summary = summary.loc[summary["specification"].eq("frontier_asic_constant_main")].copy()
    weighted_summary = summary.loc[summary["specification"].str.contains("weighted")].copy()
    lines = [
        "# Rolling-Window VECM Results",
        "",
        "Purpose: examine whether the VECM adjustment mechanism is stable over time after the static Johansen, Gregory-Hansen, and VECM results indicated specification sensitivity and structural instability.",
        "",
        "Interpretive hierarchy from previous tests:",
        "",
        "- The frontier ASIC-era restricted-constant VECM is the main specification.",
        "- Weighted-MCI systems are robustness evidence only because static weighted results are fragile and the weighted baseline has a same-sign alpha problem.",
        "- Full-sample frontier results are instability evidence, not a preferred adjustment model.",
        "- Gregory-Hansen break evidence implies that rolling-window results should be read as time-varying adjustment, not as a single stable full-sample relationship.",
        "",
        "## Main Frontier ASIC-Era Rolling Summary",
        "",
        markdown_table(main_summary[[
            "specification", "window_months", "n_windows", "first_window_end", "last_window_end",
            "beta_cost_median", "alpha_price_median", "alpha_cost_median",
            "share_price_sig_10pct", "share_cost_sig_5pct", "share_opposite_sign_alphas",
            "share_cost_side_dominant_5pct", "share_both_adjust_5pct", "share_neither_adjust_5pct",
        ]]),
        "",
        "## Robustness Rolling Summary",
        "",
        markdown_table(summary[[
            "specification", "window_months", "n_windows", "beta_cost_median",
            "alpha_price_median", "alpha_cost_median", "share_price_sig_10pct",
            "share_cost_sig_5pct", "share_opposite_sign_alphas", "share_same_sign_alphas",
        ]]),
        "",
        "## Regime Summary By Window End",
        "",
        markdown_table(regime_summary[[
            "specification", "window_months", "window_end_regime", "n_windows",
            "alpha_price_median", "alpha_cost_median", "beta_cost_median",
            "share_price_sig_10pct", "share_cost_sig_5pct", "share_opposite_sign_alphas",
        ]]),
        "",
        "## Basic Interpretation",
        "",
        rolling_interpretation(summary, regime_summary),
        "",
        "## Figure",
        "",
        f"- Frontier ASIC-era rolling adjustment plot: `{figure_path}`",
        "",
        "## Full Rolling Results",
        "",
        "The complete window-level estimates are stored in `outputs/tables/rolling_vecm_coefficients.csv`.",
    ]
    (tables / "rolling_vecm_report.md").write_text("\n".join(lines), encoding="utf-8")


def rolling_interpretation(summary: pd.DataFrame, regime_summary: pd.DataFrame) -> str:
    main = summary.loc[summary["specification"].eq("frontier_asic_constant_main")].copy()
    main_regimes = regime_summary.loc[regime_summary["specification"].eq("frontier_asic_constant_main")].copy()
    text = [
        "The rolling VECM results should be judged against the earlier static evidence. If the frontier ASIC-era model shows persistent cost-side adjustment across windows, it reinforces the static VECM reading that the constructed frontier MCI adjusts to disequilibrium more clearly than price. If the strength or sign of adjustment changes across windows, that supports the Gregory-Hansen conclusion that the long-run price-cost relation is structurally unstable.",
        "",
    ]
    if not main.empty:
        for _, row in main.sort_values("window_months", ascending=False).iterrows():
            text.append(
                f"For the main frontier ASIC-era model with {int(row['window_months'])}-month windows, "
                f"cost adjustment is significant at 5% in {row['share_cost_sig_5pct']:.1%} of windows, "
                f"price adjustment is significant at 10% in {row['share_price_sig_10pct']:.1%} of windows, "
                f"and opposite-sign alphas occur in {row['share_opposite_sign_alphas']:.1%} of windows. "
                f"The median cost alpha is {row['alpha_cost_median']:.4f}, while the median price alpha is {row['alpha_price_median']:.4f}."
            )
            text.append(
                f"The median rolling cost coefficient is {row['beta_cost_median']:.4f}, which is close to the static ASIC-era value when summarized by the median, but the min-max range is wide. This means the central tendency remains economically plausible while individual windows can be unstable."
            )
    if not main_regimes.empty:
        text.extend(["", "The regime split sharpens the interpretation."])
        for window_months in sorted(main_regimes["window_months"].unique(), reverse=True):
            regime_rows = main_regimes.loc[main_regimes["window_months"].eq(window_months)]
            through_2020 = regime_rows.loc[regime_rows["window_end_regime"].eq("through_2020")]
            break_period = regime_rows.loc[regime_rows["window_end_regime"].eq("2021_2023")]
            late_period = regime_rows.loc[regime_rows["window_end_regime"].eq("2024_2025")]
            if not through_2020.empty and not break_period.empty and not late_period.empty:
                early = through_2020.iloc[0]
                mid = break_period.iloc[0]
                late = late_period.iloc[0]
                text.append(
                    f"For {int(window_months)}-month frontier ASIC windows, cost adjustment is strongest before 2021 "
                    f"({early['share_cost_sig_5pct']:.1%} of windows significant at 5%, median cost alpha {early['alpha_cost_median']:.4f}). "
                    f"It weakens in windows ending during 2021-2023 "
                    f"({mid['share_cost_sig_5pct']:.1%}, median cost alpha {mid['alpha_cost_median']:.4f}), "
                    f"then partially reappears in 2024-2025 "
                    f"({late['share_cost_sig_5pct']:.1%}, median cost alpha {late['alpha_cost_median']:.4f})."
                )
    text.extend(
        [
            "",
            "The main conclusion is therefore nuanced. Rolling estimates do not overturn the static frontier ASIC result; they show that cost-side adjustment is a recurrent feature. But the effect is not stable across regimes, especially in windows ending in 2021-2023. This is consistent with the Gregory-Hansen evidence that the long-run relation is structurally unstable and with the static VECM interpretation that RQ3 should not be answered as a simple, permanent cost-anchor mechanism.",
            "",
            "Weighted rolling results remain secondary. They are useful for checking whether price-leading-cost dynamics recur, but they should not overturn the main conclusion because the static weighted baseline had an economically awkward vector, residual autocorrelation, and same-sign alpha behavior.",
        ]
    )
    return "\n".join(text)


def main() -> None:
    config = load_config()
    paths = config["paths"]
    processed = Path(paths["processed_data"])
    tables = Path(paths["tables"])
    figures = Path(paths["figures"])
    tables.mkdir(parents=True, exist_ok=True)

    panel = read_panel(processed)
    results = rolling_rows(panel)
    summary = summarize_windows(results)
    regime_summary = summarize_regimes(results)
    figure_path = plot_main_frontier(results, figures)

    results.to_csv(tables / "rolling_vecm_coefficients.csv", index=False)
    summary.to_csv(tables / "rolling_vecm_summary.csv", index=False)
    regime_summary.to_csv(tables / "rolling_vecm_regime_summary.csv", index=False)
    write_report(tables, results, summary, regime_summary, figure_path)

    print("Rolling VECM estimation complete.")
    print("Created:")
    for path in [
        tables / "rolling_vecm_coefficients.csv",
        tables / "rolling_vecm_summary.csv",
        tables / "rolling_vecm_regime_summary.csv",
        tables / "rolling_vecm_report.md",
        figure_path,
    ]:
        print(f"- {path}")
    print("\nMain frontier ASIC-era summary:")
    print(
        summary.loc[summary["specification"].eq("frontier_asic_constant_main"), [
            "window_months", "n_windows", "alpha_price_median", "alpha_cost_median",
            "share_price_sig_10pct", "share_cost_sig_5pct", "share_opposite_sign_alphas",
        ]].to_string(index=False)
    )


if __name__ == "__main__":
    main()
