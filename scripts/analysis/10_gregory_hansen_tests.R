#!/usr/bin/env Rscript

# Gregory-Hansen structural-break cointegration tests for the thesis.
# Uses R package COINT::GHansen because Python does not provide a reliable
# thesis-ready Gregory-Hansen implementation. Note: urca::ca.po is Phillips-
# Ouliaris, not Gregory-Hansen.

suppressPackageStartupMessages({
  library(COINT)
})

ROOT <- Sys.getenv("THESIS_ANALYSIS_ROOT", unset = getwd())
PANEL_PATH <- file.path(ROOT, "data/processed/monthly/monthly_master_panel.csv")
TABLES_DIR <- file.path(ROOT, "outputs/tables")

SAMPLES <- list(
  baseline_2010_08 = "2010-08-01",
  asic_robustness_2014_01 = "2014-01-01"
)
END_MONTH <- "2025-12-01"
SYSTEMS <- list(
  weighted = "log_mci_weighted",
  frontier = "log_mci_frontier"
)
MODEL_LABELS <- c(
  `1` = "C_level_shift",
  `2` = "C_T_level_shift_with_trend",
  `3` = "C_S_regime_shift",
  `4` = "regime_and_trend_shift"
)
TEST_LABELS <- c(
  ADF_t = "ADF*",
  PP_Zt = "Zt*",
  PP_Za = "Za*"
)
TRIM <- 0.1
USE <- c("nw", "ba")

panel <- read.csv(PANEL_PATH, stringsAsFactors = FALSE)
panel$month <- as.Date(panel$month)

dir.create(TABLES_DIR, recursive = TRUE, showWarnings = FALSE)

run_one <- function(data, system_name, cost_var, sample_name, sample_start, model_id) {
  y <- data$log_bitcoin_market_price_usd
  x <- data[[cost_var]]
  gh <- GHansen(y = y, x = x, model = model_id, trim = TRIM, use = USE)
  result <- as.data.frame(gh$result)
  result$test <- rownames(result)
  rownames(result) <- NULL
  names(result) <- gsub("%", "pct", names(result), fixed = TRUE)
  names(result) <- gsub(" ", "_", names(result), fixed = TRUE)

  result$system <- system_name
  result$sample <- sample_name
  result$sample_start <- as.character(sample_start)
  result$sample_end <- END_MONTH
  result$nobs <- nrow(data)
  result$dependent_variable <- "log_bitcoin_market_price_usd"
  result$cost_variable <- cost_var
  result$model_id <- model_id
  result$model <- unname(MODEL_LABELS[as.character(model_id)])
  result$trim <- TRIM
  result$lrv_bandwidth <- USE[1]
  result$lrv_kernel <- USE[2]
  result$test_label <- unname(TEST_LABELS[result$test])
  result$break_index <- as.integer(result$break_point)
  result$break_month <- as.character(data$month[result$break_index])
  result$reject_10pct <- result$statistics < result$`10pct`
  result$reject_5pct <- result$statistics < result$`5pct`
  result$reject_1pct <- result$statistics < result$`1pct`

  result[, c(
    "system", "sample", "sample_start", "sample_end", "nobs",
    "dependent_variable", "cost_variable", "model_id", "model",
    "test", "test_label", "statistics", "1pct", "5pct", "10pct",
    "reject_1pct", "reject_5pct", "reject_10pct",
    "break_index", "break_month", "trim", "lrv_bandwidth", "lrv_kernel"
  )]
}

rows <- list()
idx <- 1
for (sample_name in names(SAMPLES)) {
  sample_start <- as.Date(SAMPLES[[sample_name]])
  data <- subset(panel, month >= sample_start & month <= as.Date(END_MONTH))
  for (system_name in names(SYSTEMS)) {
    cost_var <- SYSTEMS[[system_name]]
    data_system <- data[, c("month", "log_bitcoin_market_price_usd", cost_var)]
    if (any(!is.finite(data_system$log_bitcoin_market_price_usd)) || any(!is.finite(data_system[[cost_var]]))) {
      stop(paste("Nonfinite values in", system_name, sample_name))
    }
    for (model_id in 1:4) {
      rows[[idx]] <- run_one(data_system, system_name, cost_var, sample_name, sample_start, model_id)
      idx <- idx + 1
    }
  }
}

results <- do.call(rbind, rows)

# Summaries: strongest statistic per system/sample/test and any rejection per model.
strongest <- do.call(rbind, lapply(split(results, list(results$system, results$sample, results$test), drop = TRUE), function(df) {
  df[which.min(df$statistics), ]
}))
rownames(strongest) <- NULL

model_summary <- aggregate(
  reject_5pct ~ system + sample + model_id + model,
  data = results,
  FUN = function(x) any(x)
)
names(model_summary)[names(model_summary) == "reject_5pct"] <- "any_test_rejects_5pct"

system_summary <- aggregate(
  reject_5pct ~ system + sample,
  data = results,
  FUN = function(x) any(x)
)
names(system_summary)[names(system_summary) == "reject_5pct"] <- "any_model_test_rejects_5pct"

write.csv(results, file.path(TABLES_DIR, "gregory_hansen_results.csv"), row.names = FALSE)
write.csv(strongest, file.path(TABLES_DIR, "gregory_hansen_strongest_by_system.csv"), row.names = FALSE)
write.csv(model_summary, file.path(TABLES_DIR, "gregory_hansen_model_summary.csv"), row.names = FALSE)
write.csv(system_summary, file.path(TABLES_DIR, "gregory_hansen_system_summary.csv"), row.names = FALSE)

markdown_table <- function(df, digits = 4) {
  fmt <- function(x) {
    if (is.numeric(x)) return(format(round(x, digits), nsmall = 0, trim = TRUE))
    as.character(x)
  }
  out <- c(
    paste0("| ", paste(names(df), collapse = " | "), " |"),
    paste0("|", paste(rep("---", ncol(df)), collapse = "|"), "|")
  )
  for (i in seq_len(nrow(df))) {
    out <- c(out, paste0("| ", paste(vapply(df[i, ], fmt, character(1)), collapse = " | "), " |"))
  }
  paste(out, collapse = "\n")
}

main_cols <- c("system", "sample", "model", "test_label", "statistics", "5pct", "reject_5pct", "break_month")
report_lines <- c(
  "# Gregory-Hansen Structural-Break Cointegration Tests",
  "",
  "Implementation:",
  "",
  paste0("- R version: `", R.version.string, "`."),
  paste0("- R package: `COINT` version `", as.character(utils::packageVersion("COINT")), "`, function `GHansen()`."),
  "- Dependent variable: `log_bitcoin_market_price_usd`.",
  "- Cost variables: `log_mci_weighted` and `log_mci_frontier`.",
  "- Samples: baseline `2010-08-01` to `2025-12-01`; ASIC robustness `2014-01-01` to `2025-12-01`.",
  "- Trimming: `0.1`.",
  "- Long-run variance setting: `use = c(\"nw\", \"ba\")`.",
  "- Note: `urca::ca.po()` is Phillips-Ouliaris, not Gregory-Hansen; it is not used as the GH test here.",
  "",
  "Model definitions from `COINT::GHansen()`:",
  "",
  "- `1`: C, level shift.",
  "- `2`: C/T, level shift with trend.",
  "- `3`: C/S, regime shift.",
  "- `4`: regime and trend shift.",
  "",
  "Null hypothesis: no cointegration. Rejection supports cointegration allowing one endogenous structural break.",
  "",
  "## Strongest Test By System/Sample/Test Family",
  "",
  markdown_table(strongest[, main_cols]),
  "",
  "## Model Summary",
  "",
  markdown_table(model_summary),
  "",
  "## System Summary",
  "",
  markdown_table(system_summary),
  "",
  "## Full Results",
  "",
  markdown_table(results[, main_cols])
)
writeLines(report_lines, file.path(TABLES_DIR, "gregory_hansen_report.md"))

cat("Gregory-Hansen tests complete.\n")
cat("Created:\n")
for (file in c(
  "gregory_hansen_results.csv",
  "gregory_hansen_strongest_by_system.csv",
  "gregory_hansen_model_summary.csv",
  "gregory_hansen_system_summary.csv",
  "gregory_hansen_report.md"
)) {
  cat("- ", file.path(TABLES_DIR, file), "\n", sep = "")
}
cat("\nSystem summary:\n")
print(system_summary)
