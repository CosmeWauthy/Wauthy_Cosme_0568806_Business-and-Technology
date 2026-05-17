from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from statsmodels.tsa.api import VAR
from statsmodels.tsa.vector_ar.vecm import coint_johansen


ANALYSIS_END_MONTH = pd.Timestamp("2025-12-01")
SAMPLES = {
    "baseline_2010_08": pd.Timestamp("2010-08-01"),
    "asic_robustness_2014_01": pd.Timestamp("2014-01-01"),
}
SYSTEMS = {
    "weighted": ["log_bitcoin_market_price_usd", "log_mci_weighted"],
    "frontier": ["log_bitcoin_market_price_usd", "log_mci_frontier"],
}
VARIABLE_LABELS = {
    "log_bitcoin_market_price_usd": "Log Bitcoin market price",
    "log_mci_weighted": "Log MCI, weighted efficiency",
    "log_mci_frontier": "Log MCI, frontier efficiency",
}
MAX_VAR_LAGS = 12
MAIN_DET_ORDER = 0
DET_ORDER_LABELS = {
    -1: "none",
    0: "constant",
    1: "linear_trend",
}
CRIT_COLUMNS = {
    "90pct": 0,
    "95pct": 1,
    "99pct": 2,
}


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "config" / "paths.yaml"
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def read_panel(processed: Path) -> pd.DataFrame:
    panel = pd.read_csv(processed / "monthly" / "monthly_master_panel.csv")
    panel["month"] = pd.to_datetime(panel["month"])
    keep = ["month", "log_bitcoin_market_price_usd", "log_mci_weighted", "log_mci_frontier"]
    return panel.loc[panel["month"].le(ANALYSIS_END_MONTH), keep].sort_values("month")


def sample_system(panel: pd.DataFrame, sample_start: pd.Timestamp, variables: list[str]) -> pd.DataFrame:
    data = panel.loc[panel["month"].between(sample_start, ANALYSIS_END_MONTH), ["month", *variables]].copy()
    expected = pd.date_range(sample_start, ANALYSIS_END_MONTH, freq="MS")
    missing_months = expected.difference(data["month"])
    if len(missing_months):
        missing = ", ".join(month.date().isoformat() for month in missing_months)
        raise ValueError(f"Missing months for sample starting {sample_start.date()}: {missing}")
    if data[variables].isna().any().any():
        raise ValueError(f"Missing values for variables {variables} in sample starting {sample_start.date()}")
    return data.set_index("month")


def selected_lag_value(value: object) -> int | None:
    if value is None:
        return None
    if pd.isna(value):
        return None
    return int(value)


def lag_selection_rows(system_name: str, sample_name: str, data: pd.DataFrame) -> tuple[list[dict], int, str]:
    selection = VAR(data).select_order(maxlags=MAX_VAR_LAGS, trend="c")
    selected = selection.selected_orders
    rows = []
    for criterion in ["aic", "bic", "hqic", "fpe"]:
        lag = selected_lag_value(selected.get(criterion))
        rows.append(
            {
                "system": system_name,
                "sample": sample_name,
                "criterion": criterion.upper(),
                "selected_var_lag_order": lag,
                "max_var_lags": MAX_VAR_LAGS,
                "trend_used_for_var_selection": "c",
            }
        )
    aic_lag = selected_lag_value(selected.get("aic"))
    if aic_lag is None:
        aic_lag = 1
        note = "AIC unavailable; set VAR lag to 1."
    elif aic_lag < 1:
        note = f"AIC selected VAR lag {aic_lag}; set to 1 so Johansen has a valid levels VAR lag."
        aic_lag = 1
    else:
        note = "AIC-selected VAR lag used."
    return rows, aic_lag, note


def rank_from_stats(stats: np.ndarray, crit_vals: np.ndarray, crit_col: int) -> int:
    rank = 0
    for idx, stat in enumerate(stats):
        if stat > crit_vals[idx, crit_col]:
            rank = idx + 1
        else:
            break
    return int(rank)


def johansen_rows(
    system_name: str,
    sample_name: str,
    data: pd.DataFrame,
    var_lag_order: int,
    det_order: int,
) -> tuple[list[dict], list[dict]]:
    k_ar_diff = max(var_lag_order - 1, 0)
    result = coint_johansen(data, det_order=det_order, k_ar_diff=k_ar_diff)
    rank_rows = []
    for row_idx, null_rank in enumerate(range(data.shape[1])):
        for test_name, stats, crits in [
            ("trace", result.lr1, result.cvt),
            ("max_eigenvalue", result.lr2, result.cvm),
        ]:
            rank_rows.append(
                {
                    "system": system_name,
                    "sample": sample_name,
                    "sample_start": data.index.min().date().isoformat(),
                    "sample_end": data.index.max().date().isoformat(),
                    "nobs_levels": int(data.shape[0]),
                    "variables": ", ".join(data.columns),
                    "det_order": det_order,
                    "deterministic": DET_ORDER_LABELS[det_order],
                    "var_lag_order_levels": int(var_lag_order),
                    "k_ar_diff": int(k_ar_diff),
                    "test": test_name,
                    "null_rank": int(null_rank),
                    "alternative": f"rank > {null_rank}",
                    "statistic": float(stats[row_idx]),
                    "critical_90pct": float(crits[row_idx, CRIT_COLUMNS["90pct"]]),
                    "critical_95pct": float(crits[row_idx, CRIT_COLUMNS["95pct"]]),
                    "critical_99pct": float(crits[row_idx, CRIT_COLUMNS["99pct"]]),
                    "reject_95pct": bool(stats[row_idx] > crits[row_idx, CRIT_COLUMNS["95pct"]]),
                }
            )
    vector_rows = []
    for vec_idx in range(data.shape[1]):
        beta = result.evec[:, vec_idx].astype(float)
        if abs(beta[0]) > 1e-12:
            beta = beta / beta[0]
        vector_rows.append(
            {
                "system": system_name,
                "sample": sample_name,
                "det_order": det_order,
                "deterministic": DET_ORDER_LABELS[det_order],
                "var_lag_order_levels": int(var_lag_order),
                "k_ar_diff": int(k_ar_diff),
                "eigenvector_index": int(vec_idx + 1),
                "normalized_on": data.columns[0],
                data.columns[0]: float(beta[0]),
                data.columns[1]: float(beta[1]),
                "cointegration_relation": f"{data.columns[0]} + ({beta[1]:.6f})*{data.columns[1]}",
            }
        )
    return rank_rows, vector_rows


def summarize_ranks(rank_tests: pd.DataFrame, lag_notes: dict[tuple[str, str], str]) -> pd.DataFrame:
    rows = []
    for (system, sample, det_order), group in rank_tests.groupby(["system", "sample", "det_order"], sort=False):
        trace = group.loc[group["test"].eq("trace")].sort_values("null_rank")
        maxeig = group.loc[group["test"].eq("max_eigenvalue")].sort_values("null_rank")
        trace_rank = rank_from_stats(trace["statistic"].to_numpy(), trace[["critical_90pct", "critical_95pct", "critical_99pct"]].to_numpy(), 1)
        maxeig_rank = rank_from_stats(maxeig["statistic"].to_numpy(), maxeig[["critical_90pct", "critical_95pct", "critical_99pct"]].to_numpy(), 1)
        chosen_rank = trace_rank if trace_rank == maxeig_rank else min(trace_rank, maxeig_rank)
        rows.append(
            {
                "system": system,
                "sample": sample,
                "sample_start": group["sample_start"].iloc[0],
                "sample_end": group["sample_end"].iloc[0],
                "nobs_levels": int(group["nobs_levels"].iloc[0]),
                "det_order": int(det_order),
                "deterministic": group["deterministic"].iloc[0],
                "var_lag_order_levels": int(group["var_lag_order_levels"].iloc[0]),
                "k_ar_diff": int(group["k_ar_diff"].iloc[0]),
                "trace_rank_95pct": int(trace_rank),
                "maxeig_rank_95pct": int(maxeig_rank),
                "chosen_rank_95pct": int(chosen_rank),
                "cointegration_supported_rank1": bool(chosen_rank == 1),
                "main_specification": bool(det_order == MAIN_DET_ORDER),
                "lag_selection_note": lag_notes[(system, sample)],
                "rank_note": rank_note(trace_rank, maxeig_rank, chosen_rank),
            }
        )
    return pd.DataFrame(rows)


def rank_note(trace_rank: int, maxeig_rank: int, chosen_rank: int) -> str:
    if trace_rank == maxeig_rank == 1:
        return "Trace and max-eigenvalue both support one cointegrating relation."
    if trace_rank == maxeig_rank == 0:
        return "Trace and max-eigenvalue both fail to support cointegration."
    if trace_rank == maxeig_rank:
        return f"Trace and max-eigenvalue agree on rank {trace_rank}."
    return f"Trace rank {trace_rank} and max-eigenvalue rank {maxeig_rank} differ; conservative chosen rank {chosen_rank}."


def markdown_table(df: pd.DataFrame, float_digits: int | None = None) -> str:
    def fmt(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            return f"{value:.{float_digits}f}" if float_digits is not None else str(value)
        return str(value)
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt(row[col]) for col in cols) + " |")
    return "\n".join(lines)



def lag_criterion_sensitivity(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sample_name, sample_start in SAMPLES.items():
        for system_name, variables in SYSTEMS.items():
            data = sample_system(panel, sample_start, variables)
            selection = VAR(data).select_order(maxlags=MAX_VAR_LAGS, trend="c")
            for criterion in ["aic", "bic", "hqic", "fpe"]:
                selected_lag = selected_lag_value(selection.selected_orders.get(criterion))
                if selected_lag is None or selected_lag < 1:
                    selected_lag = 1
                for det_order in [-1, 0, 1]:
                    rr, _vv = johansen_rows(system_name, sample_name, data, selected_lag, det_order)
                    temp = pd.DataFrame(rr)
                    trace = temp.loc[temp["test"].eq("trace")].sort_values("null_rank")
                    maxeig = temp.loc[temp["test"].eq("max_eigenvalue")].sort_values("null_rank")
                    trace_rank = rank_from_stats(
                        trace["statistic"].to_numpy(),
                        trace[["critical_90pct", "critical_95pct", "critical_99pct"]].to_numpy(),
                        1,
                    )
                    maxeig_rank = rank_from_stats(
                        maxeig["statistic"].to_numpy(),
                        maxeig[["critical_90pct", "critical_95pct", "critical_99pct"]].to_numpy(),
                        1,
                    )
                    chosen_rank = trace_rank if trace_rank == maxeig_rank else min(trace_rank, maxeig_rank)
                    rows.append(
                        {
                            "system": system_name,
                            "sample": sample_name,
                            "sample_start": data.index.min().date().isoformat(),
                            "criterion": criterion.upper(),
                            "det_order": det_order,
                            "deterministic": DET_ORDER_LABELS[det_order],
                            "var_lag_order_levels": int(selected_lag),
                            "k_ar_diff": int(max(selected_lag - 1, 0)),
                            "trace_rank_95pct": int(trace_rank),
                            "maxeig_rank_95pct": int(maxeig_rank),
                            "chosen_rank_95pct": int(chosen_rank),
                            "cointegration_supported_rank1": bool(chosen_rank == 1),
                            "rank_note": rank_note(trace_rank, maxeig_rank, chosen_rank),
                        }
                    )
    return pd.DataFrame(rows)


def write_report(
    output_path: Path,
    rank_summary: pd.DataFrame,
    rank_tests: pd.DataFrame,
    lag_selection: pd.DataFrame,
    vectors: pd.DataFrame,
    lag_sensitivity: pd.DataFrame,
) -> None:
    main_summary = rank_summary.loc[rank_summary["main_specification"]].copy()
    main_vectors = vectors.loc[vectors["det_order"].eq(MAIN_DET_ORDER) & vectors["eigenvector_index"].eq(1)].copy()
    main_tests = rank_tests.loc[rank_tests["det_order"].eq(MAIN_DET_ORDER)].copy()
    lines = [
        "# Johansen Cointegration Tests",
        "",
        "Main specification:",
        "",
        f"- VAR lag order selected by AIC on levels with intercept and maximum `{MAX_VAR_LAGS}` monthly lags.",
        "- Johansen test uses a constant deterministic term (`det_order = 0`).",
        "- `k_ar_diff = selected VAR lag order - 1`.",
        "- No-deterministic and linear-trend specifications are retained as deterministic-term sensitivity checks.",
        "",
        "## Main Rank Summary",
        "",
        markdown_table(
            main_summary[[
                "system", "sample", "sample_start", "nobs_levels", "var_lag_order_levels", "k_ar_diff",
                "trace_rank_95pct", "maxeig_rank_95pct", "chosen_rank_95pct",
                "cointegration_supported_rank1", "rank_note",
            ]]
        ),
        "",
        "## Main Cointegrating Vectors",
        "",
        markdown_table(main_vectors, float_digits=6),
        "",
        "## Main Test Statistics",
        "",
        markdown_table(
            main_tests[[
                "system", "sample", "test", "null_rank", "statistic", "critical_95pct", "reject_95pct"
            ]],
            float_digits=4,
        ),
        "",
        "## Lag Selection",
        "",
        markdown_table(lag_selection),
        "",
        "## Deterministic-Term Sensitivity Summary",
        "",
        markdown_table(
            rank_summary[[
                "system", "sample", "deterministic", "var_lag_order_levels", "trace_rank_95pct",
                "maxeig_rank_95pct", "chosen_rank_95pct", "cointegration_supported_rank1", "rank_note"
            ]]
        ),
        "",
        "## Lag-Criterion Sensitivity Summary",
        "",
        markdown_table(
            lag_sensitivity[[
                "system", "sample", "criterion", "deterministic", "var_lag_order_levels",
                "trace_rank_95pct", "maxeig_rank_95pct", "chosen_rank_95pct",
                "cointegration_supported_rank1", "rank_note"
            ]]
        ),
        "",
        "Interpretation note:",
        "",
        "- A rank of `1` in a bivariate system supports one cointegrating relation.",
        "- A rank of `0` does not support cointegration under that specification.",
        "- A rank of `2` would imply both variables are stationary in levels and should be treated cautiously given the prior integration-order decision.",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    config = load_config()
    paths = config["paths"]
    processed = Path(paths["processed_data"])
    tables = Path(paths["tables"])
    tables.mkdir(parents=True, exist_ok=True)

    panel = read_panel(processed)
    lag_rows = []
    rank_rows = []
    vector_rows = []
    lag_notes = {}

    for sample_name, sample_start in SAMPLES.items():
        for system_name, variables in SYSTEMS.items():
            data = sample_system(panel, sample_start, variables)
            rows, var_lag_order, note = lag_selection_rows(system_name, sample_name, data)
            lag_rows.extend(rows)
            lag_notes[(system_name, sample_name)] = note
            for det_order in [-1, 0, 1]:
                rr, vv = johansen_rows(system_name, sample_name, data, var_lag_order, det_order)
                rank_rows.extend(rr)
                vector_rows.extend(vv)

    lag_selection = pd.DataFrame(lag_rows)
    rank_tests = pd.DataFrame(rank_rows)
    vectors = pd.DataFrame(vector_rows)
    rank_summary = summarize_ranks(rank_tests, lag_notes)
    lag_sensitivity = lag_criterion_sensitivity(panel)

    lag_selection.to_csv(tables / "johansen_lag_selection.csv", index=False)
    rank_tests.to_csv(tables / "johansen_rank_tests.csv", index=False)
    vectors.to_csv(tables / "johansen_cointegrating_vectors.csv", index=False)
    rank_summary.to_csv(tables / "johansen_rank_summary.csv", index=False)
    lag_sensitivity.to_csv(tables / "johansen_lag_criterion_sensitivity.csv", index=False)
    write_report(tables / "johansen_cointegration_report.md", rank_summary, rank_tests, lag_selection, vectors, lag_sensitivity)

    print("Johansen cointegration tests complete.")
    print("Created:")
    for path in [
        tables / "johansen_lag_selection.csv",
        tables / "johansen_rank_tests.csv",
        tables / "johansen_cointegrating_vectors.csv",
        tables / "johansen_rank_summary.csv",
        tables / "johansen_lag_criterion_sensitivity.csv",
        tables / "johansen_cointegration_report.md",
    ]:
        print(f"- {path}")
    print("\nMain specification summary:")
    print(rank_summary.loc[rank_summary["main_specification"], [
        "system", "sample", "var_lag_order_levels", "trace_rank_95pct", "maxeig_rank_95pct",
        "chosen_rank_95pct", "cointegration_supported_rank1", "rank_note",
    ]].to_string(index=False))


if __name__ == "__main__":
    main()
