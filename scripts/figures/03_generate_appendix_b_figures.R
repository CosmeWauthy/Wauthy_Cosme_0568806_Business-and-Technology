#!/usr/bin/env Rscript

# Appendix B figure generator. The rolling figures exclude the 48-month
# ASIC-era rolling VECM figure already used in the main text.

ROOT <- Sys.getenv("THESIS_ANALYSIS_ROOT", unset = getwd())
FIG_DIR <- file.path(ROOT, "outputs/figures")

dir.create(FIG_DIR, recursive = TRUE, showWarnings = FALSE)

rolling_path <- file.path(ROOT, "outputs/tables/rolling_vecm_coefficients.csv")
panel_path <- file.path(ROOT, "data/processed/monthly/monthly_master_panel.csv")
gh_path <- file.path(ROOT, "outputs/tables/gregory_hansen_results.csv")

china_relocation <- as.Date("2021-06-01")
halving_2024 <- as.Date("2024-04-01")
disruption_start <- as.Date("2021-06-01")
disruption_end <- as.Date("2023-12-01")

theme_cols <- list(
  beta = "#1b4f72",
  alpha_price = "#8e2c2c",
  alpha_cost = "#2d6a4f",
  event = "grey25",
  grid = "grey88",
  static = "grey45"
)

rolling_specs <- list(
  frontier_asic = list(
    specification = "frontier_asic_constant_main",
    header = "Frontier ASIC-era specification",
    static_beta = -0.942913,
    static_label = "Frontier static beta = -0.943"
  ),
  weighted_asic = list(
    specification = "weighted_asic_linear_trend_sensitivity",
    header = "Weighted MCI ASIC-era specification",
    static_beta = -0.223019,
    static_label = "Weighted static beta = -0.223"
  ),
  frontier_full = list(
    specification = "frontier_baseline_none_sensitivity",
    header = "Frontier full-sample specification",
    static_beta = -0.394459,
    static_label = "Frontier static beta = -0.394"
  ),
  weighted_full = list(
    specification = "weighted_baseline_parsimonious_constant",
    header = "Weighted MCI full-sample specification",
    static_beta = 16.264717,
    static_label = "Weighted static beta = 16.265"
  )
)

add_event_overlays <- function() {
  rect(
    disruption_start, par("usr")[3],
    disruption_end, par("usr")[4],
    col = adjustcolor("grey80", alpha.f = 0.35),
    border = NA
  )
  grid(nx = NA, ny = NULL, col = theme_cols$grid, lty = 1)
  abline(v = china_relocation, col = theme_cols$event, lwd = 1, lty = 3)
  abline(v = halving_2024, col = theme_cols$event, lwd = 1, lty = 2)
}

date_ticks <- function(x_limits) {
  start_year <- as.integer(format(x_limits[1], "%Y"))
  end_year <- as.integer(format(x_limits[2], "%Y")) + 1
  seq(as.Date(sprintf("%d-01-01", start_year)), as.Date(sprintf("%d-01-01", end_year)), by = "1 year")
}

panel_ylim <- function(y, static_line = NULL) {
  range_input <- y[is.finite(y)]
  if (!is.null(static_line)) range_input <- c(range_input, static_line)
  ylim <- range(range_input, na.rm = TRUE)
  pad <- diff(ylim) * 0.08
  if (!is.finite(pad) || pad == 0) pad <- 0.1
  c(ylim[1] - pad, ylim[2] + pad)
}

plot_rolling_panel <- function(data, variable, ylab, col, x_limits, ticks, static_line = NULL, date_label = FALSE) {
  par(mar = c(3.45, 4.45, 1.05, 0.9), xpd = FALSE)
  x <- data$window_end
  y <- data[[variable]]
  plot(
    x, y,
    type = "l",
    lwd = 2,
    col = col,
    xlab = "",
    ylab = ylab,
    ylim = panel_ylim(y, static_line),
    xlim = x_limits,
    xaxt = "n"
  )
  add_event_overlays()
  lines(x, y, lwd = 2, col = col)
  abline(h = 0, col = "grey35", lwd = 1)
  if (!is.null(static_line)) {
    abline(h = static_line, col = theme_cols$static, lwd = 1.15, lty = 4)
  }
  axis.Date(1, at = ticks, format = "%Y", cex.axis = 0.78)
  if (date_label) {
    mtext("Date", side = 1, line = 2.35, cex = 0.78)
  }
  box()
}

draw_static_beta_panel_legend <- function(label) {
  old_xpd <- par("xpd")
  par(mar = c(0, 0, 0, 0), xpd = NA)
  on.exit(par(xpd = old_xpd))
  plot.new()
  par(usr = c(0, 1, 0, 1))
  y <- 0.54
  segments(0.34, y, 0.46, y, col = theme_cols$static, lwd = 1.2, lty = 4)
  text(0.49, y, label, adj = c(0, 0.5), cex = 0.66, col = theme_cols$static)
}

draw_shared_rolling_legend <- function() {
  par(mar = c(0, 0, 0, 0), xpd = NA)
  plot.new()
  par(usr = c(0, 1, 0, 1))
  y <- 0.62
  cex <- 0.68
  line_len <- 0.035
  rect_w <- 0.024

  x <- 0.19
  segments(x, y, x + line_len, y, col = theme_cols$event, lwd = 1.2, lty = 3)
  text(x + line_len + 0.008, y, "China mining relocation, 2021", adj = c(0, 0.5), cex = cex)

  x <- 0.43
  segments(x, y, x + line_len, y, col = theme_cols$event, lwd = 1.2, lty = 2)
  text(x + line_len + 0.008, y, "April 2024 halving", adj = c(0, 0.5), cex = cex)

  x <- 0.61
  rect(x, y - 0.08, x + rect_w, y + 0.08, col = adjustcolor("grey80", alpha.f = 0.55), border = NA)
  text(x + rect_w + 0.008, y, "2021-2023 disruption window", adj = c(0, 0.5), cex = cex)
}

draw_note_panel <- function(note_text) {
  par(mar = c(0, 0, 0, 0), xpd = NA)
  plot.new()
  wrapped <- paste(strwrap(note_text, width = 165), collapse = "\n")
  text(0, 0.9, wrapped, adj = c(0, 1), cex = 0.62, family = "serif")
}

draw_rolling_figure <- function(output_file, figure_label, left_key, right_key, window_months, note_text) {
  rolling <- read.csv(rolling_path, stringsAsFactors = FALSE)
  rolling$window_end <- as.Date(rolling$window_end)

  left_spec <- rolling_specs[[left_key]]
  right_spec <- rolling_specs[[right_key]]

  left <- rolling[
    rolling$specification == left_spec$specification &
      rolling$window_months == window_months &
      rolling$status == "ok",
  ]
  right <- rolling[
    rolling$specification == right_spec$specification &
      rolling$window_months == window_months &
      rolling$status == "ok",
  ]

  if (nrow(left) == 0) stop("No rows found for left rolling specification.")
  if (nrow(right) == 0) stop("No rows found for right rolling specification.")

  left <- left[order(left$window_end), ]
  right <- right[order(right$window_end), ]
  x_limits <- range(c(left$window_end, right$window_end), na.rm = TRUE)
  ticks <- date_ticks(x_limits)

  png(output_file, width = 2600, height = 2500, res = 240)
  old_par <- par(no.readonly = TRUE)
  on.exit({
    par(old_par)
    dev.off()
  })

  layout(
    matrix(c(1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 10, 10), nrow = 6, byrow = TRUE),
    widths = c(1, 1),
    heights = c(1, 0.11, 1, 1, 0.16, 0.32)
  )

  par(mar = c(3.45, 4.45, 1.05, 0.9), oma = c(0, 0, 3.6, 0), family = "serif", cex = 0.84)

  plot_rolling_panel(left, "beta_cost", expression(beta[MCI]), theme_cols$beta, x_limits, ticks, left_spec$static_beta)
  mtext(left_spec$header, side = 3, line = 1.05, font = 2, cex = 0.88)

  plot_rolling_panel(right, "beta_cost", expression(beta[MCI]), theme_cols$beta, x_limits, ticks, right_spec$static_beta)
  mtext(right_spec$header, side = 3, line = 1.05, font = 2, cex = 0.88)

  draw_static_beta_panel_legend(left_spec$static_label)
  draw_static_beta_panel_legend(right_spec$static_label)

  plot_rolling_panel(left, "alpha_price", expression(alpha[price]), theme_cols$alpha_price, x_limits, ticks)
  plot_rolling_panel(right, "alpha_price", expression(alpha[price]), theme_cols$alpha_price, x_limits, ticks)

  plot_rolling_panel(left, "alpha_cost", expression(alpha[MCI]), theme_cols$alpha_cost, x_limits, ticks, date_label = TRUE)
  plot_rolling_panel(right, "alpha_cost", expression(alpha[MCI]), theme_cols$alpha_cost, x_limits, ticks, date_label = TRUE)

  draw_shared_rolling_legend()
  draw_note_panel(note_text)

  mtext(figure_label, side = 3, outer = TRUE, line = 2.1, font = 2, cex = 1.0)
}

draw_level_diff_figure <- function(output_file) {
  panel <- read.csv(panel_path, stringsAsFactors = FALSE)
  panel$month <- as.Date(panel$month)
  panel <- panel[panel$month >= as.Date("2010-08-01") & panel$month <= as.Date("2025-12-01"), ]

  vars <- c("log_bitcoin_market_price_usd", "log_mci_weighted", "log_mci_frontier")
  level_labels <- c("Log Bitcoin price", "Log weighted MCI", "Log frontier MCI")
  diff_labels <- c(
    "First difference of log Bitcoin price",
    "First difference of log weighted MCI",
    "First difference of log frontier MCI"
  )
  cols <- c(theme_cols$beta, theme_cols$alpha_cost, theme_cols$alpha_price)
  ticks <- seq(as.Date("2011-01-01"), as.Date("2026-01-01"), by = "2 years")

  png(output_file, width = 2600, height = 2100, res = 240)
  old_par <- par(no.readonly = TRUE)
  on.exit({
    par(old_par)
    dev.off()
  })

  layout(matrix(c(1, 2, 3, 4, 5, 6, 7, 7), nrow = 4, byrow = TRUE), widths = c(1, 1), heights = c(1, 1, 1, 0.18))
  par(mar = c(2.8, 5.25, 1.15, 0.9), oma = c(0, 0, 5.1, 0), family = "serif", cex = 0.84)

  for (i in seq_along(vars)) {
    y <- panel[[vars[i]]]
    plot(panel$month, y, type = "l", lwd = 2, col = cols[i], xlab = "", ylab = level_labels[i], xaxt = "n")
    grid(nx = NA, ny = NULL, col = theme_cols$grid, lty = 1)
    lines(panel$month, y, lwd = 2, col = cols[i])
    axis.Date(1, at = ticks, format = "%Y", cex.axis = 0.78)
    box()
    if (i == 1) mtext("Levels", side = 3, line = 0.4, font = 2, cex = 0.88)

    dy <- diff(y)
    dx <- panel$month[-1]
    plot(dx, dy, type = "l", lwd = 2, col = cols[i], xlab = "", ylab = diff_labels[i], xaxt = "n")
    grid(nx = NA, ny = NULL, col = theme_cols$grid, lty = 1)
    lines(dx, dy, lwd = 2, col = cols[i])
    abline(h = 0, col = "grey35", lwd = 1)
    axis.Date(1, at = ticks, format = "%Y", cex.axis = 0.78)
    box()
    if (i == 1) mtext("First differences", side = 3, line = 0.4, font = 2, cex = 0.88)
  }

  draw_note_panel("Note. The figure displays log Bitcoin price, log weighted MCI, and log frontier MCI in levels and first differences over the analysis sample.")

  mtext("Figure B4. Levels and first differences of the core log variables.", side = 3, outer = TRUE, line = 3.45, font = 2, cex = 1.0)
}

draw_gh_timeline <- function(output_file) {
  gh <- read.csv(gh_path, stringsAsFactors = FALSE)
  gh$break_month <- as.Date(gh$break_month)
  gh <- gh[gh$reject_5pct == TRUE & !is.na(gh$break_month), ]

  gh$system_sample <- paste(
    ifelse(gh$system == "frontier", "Frontier", "Weighted"),
    ifelse(gh$sample == "asic_robustness_2014_01", "ASIC era", "full sample"),
    sep = " - "
  )
  groups <- rev(c(
    "Frontier - full sample",
    "Weighted - full sample",
    "Frontier - ASIC era",
    "Weighted - ASIC era"
  ))
  gh$y <- match(gh$system_sample, groups)

  model_cols <- c(
    C_level_shift = "#1b4f72",
    C_T_level_shift_with_trend = "#8e2c2c",
    C_S_regime_shift = "#2d6a4f",
    regime_and_trend_shift = "#6b4c9a"
  )
  model_labels <- c(
    C_level_shift = "Level shift",
    C_T_level_shift_with_trend = "Level shift with trend",
    C_S_regime_shift = "Regime shift",
    regime_and_trend_shift = "Regime and trend shift"
  )

  xlim <- as.Date(c("2013-01-01", "2025-02-01"))
  ticks <- seq(as.Date("2013-01-01"), as.Date("2025-01-01"), by = "1 year")

  png(output_file, width = 2600, height = 1550, res = 240)
  old_par <- par(no.readonly = TRUE)
  on.exit({
    par(old_par)
    dev.off()
  })

  layout(matrix(c(1, 2), nrow = 2), heights = c(1, 0.22))
  par(mar = c(4.0, 9.5, 2.0, 1.0), oma = c(0, 0, 5.1, 0), family = "serif", cex = 0.86)
  plot(
    xlim, c(0.5, length(groups) + 0.5),
    type = "n",
    xlab = "Estimated break date",
    ylab = "",
    yaxt = "n",
    xaxt = "n"
  )
  rect(disruption_start, par("usr")[3], disruption_end, par("usr")[4], col = adjustcolor("grey80", alpha.f = 0.35), border = NA)
  grid(nx = NA, ny = NULL, col = theme_cols$grid, lty = 1)
  axis.Date(1, at = ticks, format = "%Y", cex.axis = 0.78)
  axis(2, at = seq_along(groups), labels = groups, las = 1, tick = FALSE)
  abline(v = china_relocation, col = theme_cols$event, lwd = 1, lty = 3)
  abline(v = halving_2024, col = theme_cols$event, lwd = 1, lty = 2)
  points(gh$break_month, gh$y, pch = 19, cex = 1.25, col = model_cols[gh$model])
  box()

  par(mar = c(0, 0, 0, 0), xpd = NA)
  plot.new()
  par(usr = c(0, 1, 0, 1))

  y <- 0.76
  cex <- 0.68
  point_x <- c(0.30, 0.45, 0.61, 0.77)
  text_x <- point_x + 0.018
  points(point_x, rep(y, length(point_x)), pch = 19, cex = 0.85, col = model_cols)
  text(text_x, rep(y, length(text_x)), unname(model_labels), adj = c(0, 0.5), cex = cex)

  y <- 0.42
  cex <- 0.68
  line_len <- 0.035
  rect_w <- 0.024

  x <- 0.25
  segments(x, y, x + line_len, y, col = theme_cols$event, lwd = 1.2, lty = 3)
  text(x + line_len + 0.008, y, "China mining relocation, 2021", adj = c(0, 0.5), cex = cex)

  x <- 0.47
  segments(x, y, x + line_len, y, col = theme_cols$event, lwd = 1.2, lty = 2)
  text(x + line_len + 0.008, y, "April 2024 halving", adj = c(0, 0.5), cex = cex)

  x <- 0.64
  rect(x, y - 0.08, x + rect_w, y + 0.08, col = adjustcolor("grey80", alpha.f = 0.55), border = NA)
  text(x + rect_w + 0.008, y, "2021-2023 disruption window", adj = c(0, 0.5), cex = cex)

  text(
    0,
    0.08,
    "Note. Only Gregory-Hansen specifications rejecting the null of no cointegration at the 5% level are plotted.",
    adj = c(0, 0.5),
    cex = 0.66
  )

  mtext("Figure B5. Gregory-Hansen break-date timeline.", side = 3, outer = TRUE, line = 3.45, font = 2, cex = 1.0)
  mtext("Gregory-Hansen 5% rejection break dates", side = 3, outer = TRUE, line = 2.05, cex = 0.86)
}

outputs <- c(
  B1 = file.path(FIG_DIR, "figure_B1_rolling_vecm_36m_asic.png"),
  B2 = file.path(FIG_DIR, "figure_B2_rolling_vecm_48m_fullsample.png"),
  B3 = file.path(FIG_DIR, "figure_B3_rolling_vecm_36m_fullsample.png"),
  B4 = file.path(FIG_DIR, "figure_B4_levels_first_differences.png"),
  B5 = file.path(FIG_DIR, "figure_B5_gregory_hansen_break_timeline.png")
)

draw_rolling_figure(
  outputs["B1"],
  "Figure B1. Rolling-window VECM coefficients, 36-month window, ASIC-era sample.",
  "frontier_asic",
  "weighted_asic",
  36,
  "Note. Rolling estimates are based on 36-month windows and are plotted by window end date. The ASIC-era estimation sample starts in January 2014, so the first rolling estimates appear at the end of the first completed window. The dotted vertical line marks the 2021 mining relocation, the dashed vertical line marks the April 2024 halving, and the shaded area marks the 2021-2023 disruption window used for visual interpretation, not a formally estimated break interval."
)

draw_rolling_figure(
  outputs["B2"],
  "Figure B2. Rolling-window VECM coefficients, 48-month window, full sample.",
  "frontier_full",
  "weighted_full",
  48,
  "Note. Rolling estimates are based on 48-month windows and are plotted by window end date. The full-sample estimation sample starts in August 2010, so the first rolling estimates appear at the end of the first completed window. The dotted vertical line marks the 2021 mining relocation, the dashed vertical line marks the April 2024 halving, and the shaded area marks the 2021-2023 disruption window used for visual interpretation, not a formally estimated break interval."
)

draw_rolling_figure(
  outputs["B3"],
  "Figure B3. Rolling-window VECM coefficients, 36-month window, full sample.",
  "frontier_full",
  "weighted_full",
  36,
  "Note. Rolling estimates are based on 36-month windows and are plotted by window end date. The full-sample estimation sample starts in August 2010, so the first rolling estimates appear at the end of the first completed window. The dotted vertical line marks the 2021 mining relocation, the dashed vertical line marks the April 2024 halving, and the shaded area marks the 2021-2023 disruption window used for visual interpretation, not a formally estimated break interval."
)

draw_level_diff_figure(outputs["B4"])
draw_gh_timeline(outputs["B5"])

cat("Created Appendix B figure files:\n")
for (path in outputs) {
  cat("- ", path, "\n", sep = "")
}
