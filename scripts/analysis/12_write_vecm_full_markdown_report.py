from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


REPORT_NAME = "vecm_full_markdown_report.md"


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "config" / "paths.yaml"
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def markdown_table(df: pd.DataFrame, float_digits: int = 6) -> str:
    def fmt(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            return f"{value:.{float_digits}f}"
        return str(value)

    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def read_table(tables_dir: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(tables_dir / name)


def main() -> None:
    config = load_config()
    tables_dir = Path(config["paths"]["tables"])
    tables_dir.mkdir(parents=True, exist_ok=True)

    specifications = read_table(tables_dir, "vecm_specifications.csv")
    cointegration = read_table(tables_dir, "vecm_cointegrating_relations.csv")
    adjustment = read_table(tables_dir, "vecm_adjustment_coefficients.csv")
    short_run = read_table(tables_dir, "vecm_short_run_coefficients.csv")
    diagnostics = read_table(tables_dir, "vecm_residual_diagnostics.csv")

    lines = [
        "# VECM Estimation and Adjustment-Coefficient Report",
        "",
        "## Purpose",
        "",
        "This report summarizes the rank-1 VECM estimations used to interpret how Bitcoin price and the marginal-cost index adjust toward a long-run equilibrium. The estimations follow the documented Johansen and Gregory-Hansen cointegration evidence and are limited to rank-1 candidate systems.",
        "",
        "## Basic Interpretation",
        "",
        "The strongest and most thesis-ready specification is the frontier ASIC-era VECM with a restricted constant. This model uses the frontier marginal-cost index from `2014-01` to `2025-12`, has one cointegrating relation, and passes the 12-lag residual-whiteness diagnostic. Its adjustment coefficients suggest that the constructed frontier MCI responds clearly to disequilibrium, while Bitcoin price adjustment is weaker and only marginally significant at the 10 percent level.",
        "",
        "The weighted-MCI results should be interpreted as secondary sensitivity evidence. The weighted full-sample parsimonious specification produces statistically significant adjustment coefficients, but the coefficients are very small, the cointegrating vector is economically awkward, and residual autocorrelation remains. The weighted ASIC-era trend specification gives only marginal evidence of price adjustment and no conventional evidence of weighted-MCI adjustment.",
        "",
        "Overall, the VECM stage supports a cautious interpretation: the frontier marginal-cost measure provides the clearest evidence of a long-run price-cost relation, but the adjustment mechanism is not stable across specifications. This reinforces the need for rolling-window VECM analysis.",
        "",
        "## Key Result",
        "",
        "- Primary specification: `frontier_asic_constant_main`.",
        "- Price adjustment coefficient: `-0.0457`, p-value `0.0664`, marginal at 10 percent.",
        "- Frontier MCI adjustment coefficient: `0.1563`, p-value `< 0.001`, significant at 5 percent.",
        "- Residual whiteness: fail to reject autocorrelation at 12 lags, p-value `0.7962`.",
        "- Residual normality: rejected, so inference should remain cautious.",
        "",
        "## Full Table 1: Estimated Specifications",
        "",
        markdown_table(specifications),
        "",
        "## Full Table 2: Cointegrating Relations",
        "",
        markdown_table(cointegration),
        "",
        "## Full Table 3: Adjustment Coefficients",
        "",
        markdown_table(adjustment),
        "",
        "## Full Table 4: Short-Run Coefficients",
        "",
        markdown_table(short_run),
        "",
        "## Full Table 5: Residual Diagnostics",
        "",
        markdown_table(diagnostics),
        "",
        "## Thesis-Ready Takeaway",
        "",
        "The rank-1 VECM results indicate that the frontier marginal-cost index is the most credible cost measure for adjustment-coefficient interpretation. In the cleanest ASIC-era specification, the frontier MCI adjusts strongly to the lagged equilibrium error, while Bitcoin price adjustment is weaker and only marginally significant. Weighted-MCI specifications remain useful as robustness checks, but their adjustment results are more fragile and diagnostically weaker.",
    ]

    report_path = tables_dir / REPORT_NAME
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(report_path)


if __name__ == "__main__":
    main()
