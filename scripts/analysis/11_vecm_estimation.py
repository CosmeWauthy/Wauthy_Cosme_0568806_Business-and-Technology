from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from statsmodels.tsa.vector_ar.vecm import VECM


ANALYSIS_END_MONTH = pd.Timestamp("2025-12-01")
PRICE_VAR = "log_bitcoin_market_price_usd"
SYSTEMS = {
    "weighted": "log_mci_weighted",
    "frontier": "log_mci_frontier",
}
VARIABLE_LABELS = {
    PRICE_VAR: "Log Bitcoin market price",
    "log_mci_weighted": "Log MCI, weighted efficiency",
    "log_mci_frontier": "Log MCI, frontier efficiency",
}
SPECIFICATIONS = [
    {
        "specification": "frontier_asic_constant_main",
        "system": "frontier",
        "sample": "asic_robustness_2014_01",
        "sample_start": pd.Timestamp("2014-01-01"),
        "var_lag_order_levels": 2,
        "k_ar_diff": 1,
        "coint_rank": 1,
        "deterministic": "ci",
        "deterministic_label": "restricted_constant",
        "role": "primary frontier ASIC-era VECM",
        "rationale": "Johansen trace and max-eigenvalue tests support rank 1 under the constant specification across lag criteria in the ASIC-period sample.",
    },
    {
        "specification": "weighted_baseline_parsimonious_constant",
        "system": "weighted",
        "sample": "baseline_2010_08",
        "sample_start": pd.Timestamp("2010-08-01"),
        "var_lag_order_levels": 2,
        "k_ar_diff": 1,
        "coint_rank": 1,
        "deterministic": "ci",
        "deterministic_label": "restricted_constant",
        "role": "secondary weighted full-sample VECM",
        "rationale": "BIC and HQIC select 2 VAR lags and support rank 1 under the constant specification; AIC/FPE over-parameterised 11-lag results are treated as sensitivity evidence.",
    },
    {
        "specification": "frontier_baseline_none_sensitivity",
        "system": "frontier",
        "sample": "baseline_2010_08",
        "sample_start": pd.Timestamp("2010-08-01"),
        "var_lag_order_levels": 2,
        "k_ar_diff": 1,
        "coint_rank": 1,
        "deterministic": "n",
        "deterministic_label": "none",
        "role": "frontier full-sample deterministic-term sensitivity",
        "rationale": "Full-sample frontier Johansen tests support rank 1 only without deterministic terms; constant and trend specifications return rank 2 and are not used for rank-1 VECM interpretation.",
    },
    {
        "specification": "weighted_asic_linear_trend_sensitivity",
        "system": "weighted",
        "sample": "asic_robustness_2014_01",
        "sample_start": pd.Timestamp("2014-01-01"),
        "var_lag_order_levels": 2,
        "k_ar_diff": 1,
        "coint_rank": 1,
        "deterministic": "li",
        "deterministic_label": "restricted_linear_trend",
        "role": "weighted ASIC-era deterministic-term sensitivity",
        "rationale": "Weighted ASIC-period Johansen tests support rank 1 only with a linear-trend deterministic specification, so this is retained as a weaker sensitivity case.",
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


def fit_specification(panel: pd.DataFrame, spec: dict) -> tuple[object, pd.DataFrame]:
    cost_var = SYSTEMS[spec["system"]]
    data = sample_system(panel, spec["sample_start"], cost_var)
    model = VECM(
        data,
        k_ar_diff=spec["k_ar_diff"],
        coint_rank=spec["coint_rank"],
        deterministic=spec["deterministic"],
        freq="MS",
    )
    return model.fit(), data


def scalar_or_nan(array: np.ndarray | list | None, idx: int = 0) -> float:
    if array is None:
        return np.nan
    arr = np.asarray(array, dtype=float).ravel()
    if len(arr) <= idx:
        return np.nan
    return float(arr[idx])


def make_specification_row(spec: dict, data: pd.DataFrame, result: object) -> dict:
    return {
        "specification": spec["specification"],
        "system": spec["system"],
        "sample": spec["sample"],
        "sample_start": data.index.min().date().isoformat(),
        "sample_end": data.index.max().date().isoformat(),
        "nobs_levels": int(data.shape[0]),
        "nobs_vecm": int(result.nobs),
        "variables": ", ".join(data.columns),
        "var_lag_order_levels": int(spec["var_lag_order_levels"]),
        "k_ar_diff": int(spec["k_ar_diff"]),
        "coint_rank": int(spec["coint_rank"]),
        "deterministic": spec["deterministic"],
        "deterministic_label": spec["deterministic_label"],
        "role": spec["role"],
        "rationale": spec["rationale"],
        "log_likelihood": float(result.llf),
    }


def cointegration_rows(spec: dict, data: pd.DataFrame, result: object) -> list[dict]:
    beta = np.asarray(result.beta[:, 0], dtype=float)
    if abs(beta[0]) > 1e-12:
        beta = beta / beta[0]
    rows = []
    for idx, variable in enumerate(data.columns):
        rows.append(
            {
                "specification": spec["specification"],
                "system": spec["system"],
                "sample": spec["sample"],
                "variable": variable,
                "label": VARIABLE_LABELS[variable],
                "beta": float(beta[idx]),
                "std_err": scalar_or_nan(result.stderr_beta[:, 0], idx),
                "z_stat": scalar_or_nan(result.tvalues_beta[:, 0], idx),
                "p_value": scalar_or_nan(result.pvalues_beta[:, 0], idx),
            }
        )
    det_coef = np.asarray(getattr(result, "det_coef_coint", []), dtype=float).ravel()
    det_names = []
    if len(det_coef) and "c" in spec["deterministic"]:
        det_names.append("restricted_constant")
    if len(det_coef) and "l" in spec["deterministic"]:
        det_names.append("restricted_linear_trend")
    for idx, coef in enumerate(det_coef):
        rows.append(
            {
                "specification": spec["specification"],
                "system": spec["system"],
                "sample": spec["sample"],
                "variable": det_names[idx] if idx < len(det_names) else f"deterministic_{idx + 1}",
                "label": det_names[idx] if idx < len(det_names) else f"Deterministic term {idx + 1}",
                "beta": float(coef),
                "std_err": scalar_or_nan(getattr(result, "stderr_det_coef_coint", None), idx),
                "z_stat": scalar_or_nan(getattr(result, "tvalues_det_coef_coint", None), idx),
                "p_value": scalar_or_nan(getattr(result, "pvalues_det_coef_coint", None), idx),
            }
        )
    return rows


def adjustment_rows(spec: dict, data: pd.DataFrame, result: object) -> list[dict]:
    rows = []
    alpha = np.asarray(result.alpha[:, 0], dtype=float)
    stderr = np.asarray(result.stderr_alpha[:, 0], dtype=float)
    z_stat = np.asarray(result.tvalues_alpha[:, 0], dtype=float)
    p_value = np.asarray(result.pvalues_alpha[:, 0], dtype=float)
    for idx, variable in enumerate(data.columns):
        rows.append(
            {
                "specification": spec["specification"],
                "system": spec["system"],
                "sample": spec["sample"],
                "equation": f"delta_{variable}",
                "variable": variable,
                "label": VARIABLE_LABELS[variable],
                "alpha": float(alpha[idx]),
                "std_err": float(stderr[idx]),
                "z_stat": float(z_stat[idx]),
                "p_value": float(p_value[idx]),
                "significant_5pct": bool(p_value[idx] < 0.05),
                "significant_10pct": bool(p_value[idx] < 0.10),
                "adjustment_interpretation": interpret_alpha(variable, alpha[idx], p_value[idx]),
            }
        )
    return rows


def interpret_alpha(variable: str, alpha: float, p_value: float) -> str:
    direction = "falls when the lagged equilibrium error is positive" if alpha < 0 else "rises when the lagged equilibrium error is positive"
    if p_value < 0.05:
        strength = "statistically significant at 5%"
    elif p_value < 0.10:
        strength = "marginally significant at 10%"
    else:
        strength = "not statistically significant at conventional levels"
    if variable == PRICE_VAR:
        actor = "Bitcoin price"
    elif variable == "log_mci_weighted":
        actor = "Weighted MCI"
    else:
        actor = "Frontier MCI"
    return f"{actor} {direction}; {strength}."


def short_run_rows(spec: dict, data: pd.DataFrame, result: object) -> list[dict]:
    rows = []
    gamma = np.asarray(result.gamma, dtype=float)
    stderr = np.asarray(result.stderr_gamma, dtype=float)
    z_stat = np.asarray(result.tvalues_gamma, dtype=float)
    p_value = np.asarray(result.pvalues_gamma, dtype=float)
    variables = list(data.columns)
    for equation_idx, equation_var in enumerate(variables):
        for col_idx in range(gamma.shape[1]):
            lag = col_idx // len(variables) + 1
            lagged_var = variables[col_idx % len(variables)]
            rows.append(
                {
                    "specification": spec["specification"],
                    "system": spec["system"],
                    "sample": spec["sample"],
                    "equation": f"delta_{equation_var}",
                    "lag": int(lag),
                    "lagged_difference": f"delta_{lagged_var}",
                    "coefficient": float(gamma[equation_idx, col_idx]),
                    "std_err": float(stderr[equation_idx, col_idx]),
                    "z_stat": float(z_stat[equation_idx, col_idx]),
                    "p_value": float(p_value[equation_idx, col_idx]),
                    "significant_5pct": bool(p_value[equation_idx, col_idx] < 0.05),
                }
            )
    return rows


def diagnostics_row(spec: dict, result: object) -> dict:
    try:
        whiteness = result.test_whiteness(nlags=12)
        whiteness_stat = float(whiteness.test_statistic)
        whiteness_pvalue = float(whiteness.pvalue)
        whiteness_conclusion = str(whiteness.conclusion)
    except Exception as exc:  # pragma: no cover - defensive table reporting
        whiteness_stat = np.nan
        whiteness_pvalue = np.nan
        whiteness_conclusion = f"not available: {exc}"
    try:
        normality = result.test_normality()
        normality_stat = float(normality.test_statistic)
        normality_pvalue = float(normality.pvalue)
        normality_conclusion = str(normality.conclusion)
    except Exception as exc:  # pragma: no cover - defensive table reporting
        normality_stat = np.nan
        normality_pvalue = np.nan
        normality_conclusion = f"not available: {exc}"
    return {
        "specification": spec["specification"],
        "system": spec["system"],
        "sample": spec["sample"],
        "whiteness_nlags": 12,
        "whiteness_statistic": whiteness_stat,
        "whiteness_p_value": whiteness_pvalue,
        "whiteness_conclusion": whiteness_conclusion,
        "normality_statistic": normality_stat,
        "normality_p_value": normality_pvalue,
        "normality_conclusion": normality_conclusion,
    }


def markdown_table(df: pd.DataFrame, float_digits: int | None = None) -> str:
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


def write_report(
    output_path: Path,
    specifications: pd.DataFrame,
    adjustment: pd.DataFrame,
    cointegration: pd.DataFrame,
    diagnostics: pd.DataFrame,
) -> None:
    price_adjustment = adjustment.loc[adjustment["variable"].eq(PRICE_VAR)].copy()
    cost_adjustment = adjustment.loc[~adjustment["variable"].eq(PRICE_VAR)].copy()
    lines = [
        "# Rank-1 VECM Estimation",
        "",
        "Purpose: estimate only the documented rank-1 candidate systems and interpret adjustment coefficients.",
        "",
        "Implementation:",
        "",
        "- Python `statsmodels.tsa.vector_ar.vecm.VECM`.",
        "- Dependent systems are bivariate: log Bitcoin price with one log MCI measure.",
        "- `k_ar_diff = VAR lag order - 1`; all estimated specifications use `k_ar_diff = 1`.",
        "- Constant Johansen cases are estimated as restricted constants in the cointegrating relation (`deterministic = 'ci'`).",
        "- No-deterministic sensitivity uses `deterministic = 'n'`; linear-trend sensitivity uses a restricted trend (`deterministic = 'li'`).",
        "",
        "## Estimated Specifications",
        "",
        markdown_table(
            specifications[[
                "specification", "system", "sample", "sample_start", "sample_end", "nobs_levels",
                "var_lag_order_levels", "k_ar_diff", "deterministic_label", "role",
            ]]
        ),
        "",
        "## Adjustment Coefficients",
        "",
        markdown_table(
            adjustment[[
                "specification", "equation", "alpha", "std_err", "z_stat", "p_value",
                "significant_5pct", "significant_10pct",
            ]],
            float_digits=4,
        ),
        "",
        "## Price-Adjustment Reading",
        "",
        markdown_table(
            price_adjustment[[
                "specification", "system", "sample", "alpha", "p_value", "adjustment_interpretation",
            ]],
            float_digits=4,
        ),
        "",
        "## Cost-Adjustment Reading",
        "",
        markdown_table(
            cost_adjustment[[
                "specification", "system", "sample", "alpha", "p_value", "adjustment_interpretation",
            ]],
            float_digits=4,
        ),
        "",
        "## Cointegrating Relations",
        "",
        markdown_table(
            cointegration[[
                "specification", "variable", "beta", "std_err", "z_stat", "p_value",
            ]],
            float_digits=4,
        ),
        "",
        "## Residual Diagnostics",
        "",
        markdown_table(
            diagnostics[[
                "specification", "whiteness_nlags", "whiteness_p_value",
                "whiteness_conclusion", "normality_p_value", "normality_conclusion",
            ]],
            float_digits=4,
        ),
        "",
        "Interpretation note:",
        "",
        "- A negative price adjustment coefficient means Bitcoin price tends to fall after a positive lagged equilibrium error.",
        "- A positive cost adjustment coefficient means the MCI tends to rise after that same error.",
        "- Because the cointegrating vector is normalized on log price, the error is approximately `log_price - beta_cost * log_cost + deterministic term`.",
        "- These VECM results remain specification-dependent and should be read alongside the Gregory-Hansen break evidence.",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    config = load_config()
    paths = config["paths"]
    processed = Path(paths["processed_data"])
    tables = Path(paths["tables"])
    tables.mkdir(parents=True, exist_ok=True)

    panel = read_panel(processed)
    specification_rows = []
    adjustment = []
    cointegration = []
    short_run = []
    diagnostics = []

    for spec in SPECIFICATIONS:
        result, data = fit_specification(panel, spec)
        specification_rows.append(make_specification_row(spec, data, result))
        cointegration.extend(cointegration_rows(spec, data, result))
        adjustment.extend(adjustment_rows(spec, data, result))
        short_run.extend(short_run_rows(spec, data, result))
        diagnostics.append(diagnostics_row(spec, result))

    specifications_df = pd.DataFrame(specification_rows)
    cointegration_df = pd.DataFrame(cointegration)
    adjustment_df = pd.DataFrame(adjustment)
    short_run_df = pd.DataFrame(short_run)
    diagnostics_df = pd.DataFrame(diagnostics)

    specifications_df.to_csv(tables / "vecm_specifications.csv", index=False)
    cointegration_df.to_csv(tables / "vecm_cointegrating_relations.csv", index=False)
    adjustment_df.to_csv(tables / "vecm_adjustment_coefficients.csv", index=False)
    short_run_df.to_csv(tables / "vecm_short_run_coefficients.csv", index=False)
    diagnostics_df.to_csv(tables / "vecm_residual_diagnostics.csv", index=False)
    write_report(tables / "vecm_estimation_report.md", specifications_df, adjustment_df, cointegration_df, diagnostics_df)

    print("VECM estimation complete.")
    print("Created:")
    for path in [
        tables / "vecm_specifications.csv",
        tables / "vecm_cointegrating_relations.csv",
        tables / "vecm_adjustment_coefficients.csv",
        tables / "vecm_short_run_coefficients.csv",
        tables / "vecm_residual_diagnostics.csv",
        tables / "vecm_estimation_report.md",
    ]:
        print(f"- {path}")
    print("\nAdjustment coefficients:")
    print(
        adjustment_df[[
            "specification", "equation", "alpha", "std_err", "z_stat", "p_value",
            "significant_5pct", "significant_10pct",
        ]].to_string(index=False)
    )


if __name__ == "__main__":
    main()
