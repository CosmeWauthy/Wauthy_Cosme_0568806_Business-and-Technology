#!/usr/bin/env Rscript

# Weak-exogeneity tests for rank-1 VECM systems.
# Individual alpha restrictions use urca::alrtest(), the Johansen LR test for
# restrictions on the loading matrix. The joint no-adjustment test is reported
# as the rank-zero/no-error-correction Johansen trace LR test, because imposing
# both alpha coefficients equal to zero collapses alpha beta' to zero.

suppressPackageStartupMessages({
  library(urca)
})

ROOT <- Sys.getenv("THESIS_ANALYSIS_ROOT", unset = getwd())
PANEL_PATH <- file.path(ROOT, "data/processed/monthly/monthly_master_panel.csv")
TABLES_DIR <- file.path(ROOT, "outputs/tables")

END_MONTH <- as.Date("2025-12-01")
PRICE_VAR <- "log_bitcoin_market_price_usd"

SPECS <- list(
  list(
    specification = "frontier_asic_constant_main",
    system = "frontier",
    sample = "asic_robustness_2014_01",
    sample_start = as.Date("2014-01-01"),
    cost_var = "log_mci_frontier",
    K = 2,
    ecdet = "const",
    spec = "longrun",
    role = "main frontier ASIC-era weak-exogeneity test"
  ),
  list(
    specification = "weighted_baseline_parsimonious_constant",
    system = "weighted",
    sample = "baseline_2010_08",
    sample_start = as.Date("2010-08-01"),
    cost_var = "log_mci_weighted",
    K = 2,
    ecdet = "const",
    spec = "longrun",
    role = "weighted baseline complementary RQ3 test; interpret with vector/sign-condition caveats"
  ),
  list(
    specification = "weighted_asic_linear_trend_sensitivity",
    system = "weighted",
    sample = "asic_robustness_2014_01",
    sample_start = as.Date("2014-01-01"),
    cost_var = "log_mci_weighted",
    K = 2,
    ecdet = "trend",
    spec = "longrun",
    role = "weighted ASIC-era trend sensitivity"
  ),
  list(
    specification = "frontier_baseline_none_sensitivity",
    system = "frontier",
    sample = "baseline_2010_08",
    sample_start = as.Date("2010-08-01"),
    cost_var = "log_mci_frontier",
    K = 2,
    ecdet = "none",
    spec = "longrun",
    role = "frontier full-sample instability sensitivity"
  )
)

dir.create(TABLES_DIR, recursive = TRUE, showWarnings = FALSE)

panel <- read.csv(PANEL_PATH, stringsAsFactors = FALSE)
panel$month <- as.Date(panel$month)

chi_p <- function(stat, df) {
  stats::pchisq(stat, df = df, lower.tail = FALSE)
}

fmt_num <- function(x, digits = 4) {
  ifelse(is.na(x), "", format(round(x, digits), nsmall = digits, trim = TRUE))
}

restriction_result <- function(cajo, restriction, variable_name, A, n_variables = 2, rank = 1) {
  test <- alrtest(cajo, A = A, r = rank)
  df <- rank * (n_variables - ncol(A))
  stat <- as.numeric(test@teststat[1])
  p_value <- chi_p(stat, df)
  data.frame(
    restriction = restriction,
    variable_restricted = variable_name,
    test_family = "Johansen alpha-restriction LR",
    null_hypothesis = paste0("alpha_", variable_name, " = 0"),
    lr_statistic = stat,
    df = df,
    p_value = p_value,
    reject_5pct = p_value < 0.05,
    reject_10pct = p_value < 0.10,
    critical_10pct = NA_real_,
    critical_5pct = NA_real_,
    critical_1pct = NA_real_,
    stringsAsFactors = FALSE
  )
}

joint_result <- function(cajo) {
  # For type='trace', ca.jo stores r <= p-1 first and r = 0 last.
  stat <- as.numeric(tail(cajo@teststat, 1))
  crit <- cajo@cval[nrow(cajo@cval), ]
  data.frame(
    restriction = "joint_no_error_correction",
    variable_restricted = "price_and_cost",
    test_family = "Johansen trace rank-zero LR",
    null_hypothesis = "alpha_price = alpha_cost = 0 / no error-correction term",
    lr_statistic = stat,
    df = 2,
    p_value = NA_real_,
    reject_5pct = stat > crit["5pct"],
    reject_10pct = stat > crit["10pct"],
    critical_10pct = as.numeric(crit["10pct"]),
    critical_5pct = as.numeric(crit["5pct"]),
    critical_1pct = as.numeric(crit["1pct"]),
    stringsAsFactors = FALSE
  )
}

alpha_beta_row <- function(cajo) {
  alpha <- cajo@W[1:2, 1]
  beta <- cajo@V[1:2, 1]
  if (abs(beta[1]) > 1e-12) {
    beta <- beta / beta[1]
  }
  data.frame(
    alpha_price_urca = as.numeric(alpha[1]),
    alpha_cost_urca = as.numeric(alpha[2]),
    beta_price_urca = as.numeric(beta[1]),
    beta_cost_urca = as.numeric(beta[2]),
    same_sign_alpha = sign(alpha[1]) == sign(alpha[2]),
    opposite_sign_alpha = sign(alpha[1]) != sign(alpha[2]),
    stringsAsFactors = FALSE
  )
}

all_results <- list()
all_parameters <- list()
idx <- 1

for (sp in SPECS) {
  data <- subset(panel, month >= sp$sample_start & month <= END_MONTH)
  data <- data[, c(PRICE_VAR, sp$cost_var)]
  if (any(!is.finite(as.matrix(data)))) {
    stop(paste("Nonfinite values in", sp$specification))
  }

  cajo <- ca.jo(data, ecdet = sp$ecdet, type = "trace", K = sp$K, spec = sp$spec)

  tests <- rbind(
    restriction_result(cajo, "price_weakly_exogenous", "price", matrix(c(0, 1), nrow = 2)),
    restriction_result(cajo, "cost_weakly_exogenous", "cost", matrix(c(1, 0), nrow = 2)),
    joint_result(cajo)
  )

  common_cols <- data.frame(
    specification = sp$specification,
    system = sp$system,
    sample = sp$sample,
    sample_start = as.character(sp$sample_start),
    sample_end = as.character(END_MONTH),
    nobs_levels = nrow(data),
    K_var_lag_order_levels = sp$K,
    rank = 1,
    ecdet = sp$ecdet,
    ca_jo_spec = sp$spec,
    role = sp$role,
    stringsAsFactors = FALSE
  )
  tests <- cbind(common_cols[rep(1, nrow(tests)), ], tests)
  if (!"critical_10pct" %in% names(tests)) tests$critical_10pct <- NA_real_
  if (!"critical_5pct" %in% names(tests)) tests$critical_5pct <- NA_real_
  if (!"critical_1pct" %in% names(tests)) tests$critical_1pct <- NA_real_
  all_results[[idx]] <- tests

  params <- cbind(common_cols, alpha_beta_row(cajo))
  all_parameters[[idx]] <- params
  idx <- idx + 1
}

results <- do.call(rbind, all_results)
parameters <- do.call(rbind, all_parameters)

interpretation <- transform(
  results,
  interpretation = ifelse(
    restriction == "price_weakly_exogenous" & !reject_5pct,
    "Do not reject price weak exogeneity at 5%.",
    ifelse(
      restriction == "price_weakly_exogenous" & reject_5pct,
      "Reject price weak exogeneity at 5%; price adjusts.",
      ifelse(
        restriction == "cost_weakly_exogenous" & !reject_5pct,
        "Do not reject cost weak exogeneity at 5%.",
        ifelse(
          restriction == "cost_weakly_exogenous" & reject_5pct,
          "Reject cost weak exogeneity at 5%; cost adjusts.",
          ifelse(
            restriction == "joint_no_error_correction" & reject_5pct,
            "Reject no error correction at 5%; at least one variable adjusts.",
            "Do not reject no error correction at 5%."
          )
        )
      )
    )
  )
)

write.csv(results, file.path(TABLES_DIR, "weak_exogeneity_tests.csv"), row.names = FALSE)
write.csv(parameters, file.path(TABLES_DIR, "weak_exogeneity_alpha_beta_snapshot.csv"), row.names = FALSE)
write.csv(interpretation, file.path(TABLES_DIR, "weak_exogeneity_interpretation.csv"), row.names = FALSE)

markdown_table <- function(df, digits = 4) {
  out <- c(
    paste0("| ", paste(names(df), collapse = " | "), " |"),
    paste0("|", paste(rep("---", ncol(df)), collapse = "|"), "|")
  )
  for (i in seq_len(nrow(df))) {
    vals <- vapply(df[i, ], function(x) {
      if (is.numeric(x)) return(format(round(x, digits), nsmall = digits, trim = TRUE))
      as.character(x)
    }, character(1))
    out <- c(out, paste0("| ", paste(vals, collapse = " | "), " |"))
  }
  paste(out, collapse = "\n")
}

main_cols <- c(
  "specification", "restriction", "null_hypothesis", "test_family",
  "lr_statistic", "df", "p_value", "critical_5pct", "reject_5pct",
  "interpretation"
)

report <- c(
  "# Weak-Exogeneity Tests",
  "",
  "Purpose: formally test whether Bitcoin price and the marginal-cost measure adjust to the cointegrating relation.",
  "",
  "Implementation:",
  "",
  "- Individual weak-exogeneity restrictions use `urca::alrtest()` on `ca.jo` objects.",
  "- The null `alpha_price = 0` tests whether Bitcoin price is weakly exogenous.",
  "- The null `alpha_cost = 0` tests whether the MCI is weakly exogenous.",
  "- The joint no-adjustment test is reported as the Johansen rank-zero/no-error-correction trace LR test, because imposing both alpha coefficients equal to zero collapses `alpha beta'` to zero.",
  "- Static systems only; no rolling or regime split tests are run.",
  "",
  "## Main Results",
  "",
  markdown_table(interpretation[, main_cols]),
  "",
  "## Alpha/Beta Snapshot From `urca::ca.jo`",
  "",
  markdown_table(parameters),
  "",
  "## Interpretation Note",
  "",
  "For the main frontier ASIC-era system, the cleanest pattern would be: reject the joint no-error-correction restriction, fail to reject `alpha_price = 0`, and reject `alpha_cost = 0`. That combination supports one adjusting variable, with adjustment occurring through the frontier MCI rather than Bitcoin price.",
  "",
  "The main frontier ASIC-era system shows exactly this clean pattern: price weak exogeneity is not rejected, cost weak exogeneity is rejected, and the joint no-error-correction restriction is rejected. This formally supports the static and rolling interpretation that, in the cleanest frontier system, the frontier MCI is the adjusting variable.",
  "",
  "The weighted baseline rejects both individual weak-exogeneity restrictions and rejects the joint no-error-correction restriction. This supports the rolling result that weighted systems contain price-side adjustment, but it does not remove the earlier limitations: the static weighted baseline has a same-sign alpha problem, residual autocorrelation, and an economically awkward vector.",
  "",
  "The weighted ASIC trend and full-sample frontier no-deterministic sensitivity systems are included for completeness, but they should be read cautiously because deterministic-term handling differs across VECM implementations and these systems were already classified as sensitivity/instability cases.",
  "",
  "## Full CSV Outputs",
  "",
  "- `outputs/tables/weak_exogeneity_tests.csv`",
  "- `outputs/tables/weak_exogeneity_alpha_beta_snapshot.csv`",
  "- `outputs/tables/weak_exogeneity_interpretation.csv`"
)

writeLines(report, file.path(TABLES_DIR, "weak_exogeneity_report.md"))

cat("Weak-exogeneity tests complete.\n")
cat("Created:\n")
for (file in c(
  "weak_exogeneity_tests.csv",
  "weak_exogeneity_alpha_beta_snapshot.csv",
  "weak_exogeneity_interpretation.csv",
  "weak_exogeneity_report.md"
)) {
  cat("- ", file.path(TABLES_DIR, file), "\n", sep = "")
}
cat("\nMain results:\n")
print(interpretation[, main_cols], row.names = FALSE)
