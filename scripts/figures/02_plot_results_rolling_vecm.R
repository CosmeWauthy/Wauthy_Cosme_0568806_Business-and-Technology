#!/usr/bin/env Rscript

# Main-text rolling VECM coefficient figure.

ROOT <- Sys.getenv("THESIS_ANALYSIS_ROOT", unset = getwd())
INPUT <- file.path(ROOT, "outputs/tables/rolling_vecm_coefficients.csv")
FIG_DIR <- file.path(ROOT, "outputs/figures")

dir.create(FIG_DIR, recursive = TRUE, showWarnings = FALSE)

rolling <- read.csv(INPUT, stringsAsFactors = FALSE)
rolling$window_end <- as.Date(rolling$window_end)

frontier <- rolling[
  rolling$specification == "frontier_asic_constant_main" &
    rolling$window_months == 48,
]
frontier <- frontier[order(frontier$window_end), ]

weighted <- rolling[
  rolling$specification == "weighted_asic_linear_trend_sensitivity" &
    rolling$window_months == 48,
]
weighted <- weighted[order(weighted$window_end), ]

if (nrow(frontier) == 0) {
  stop("No rows found for frontier_asic_constant_main with 48-month windows.")
}
if (nrow(weighted) == 0) {
  stop("No rows found for weighted_asic_linear_trend_sensitivity with 48-month windows.")
}

china_relocation <- as.Date("2021-06-01")
halving_2024 <- as.Date("2024-04-01")
disruption_start <- as.Date("2021-06-01")
disruption_end <- as.Date("2023-12-01")
x_limits <- range(c(frontier$window_end, weighted$window_end), na.rm = TRUE)
year_ticks <- seq(as.Date("2018-01-01"), as.Date("2026-01-01"), by = "1 year")

plot_panel <- function(data, variable, ylab, col, static_line = NULL) {
  x <- data$window_end
  y <- data[[variable]]
  range_input <- y
  if (!is.null(static_line)) range_input <- c(range_input, static_line)
  ylim <- range(range_input, na.rm = TRUE)
  pad <- diff(ylim) * 0.08
  if (!is.finite(pad) || pad == 0) pad <- 0.1
  ylim <- c(ylim[1] - pad, ylim[2] + pad)

  plot(
    x, y,
    type = "l",
    lwd = 2,
    col = col,
    xlab = "",
    ylab = ylab,
    ylim = ylim,
    xlim = x_limits,
    xaxt = "n"
  )
  rect(
    disruption_start, par("usr")[3],
    disruption_end, par("usr")[4],
    col = adjustcolor("grey80", alpha.f = 0.35),
    border = NA
  )
  grid(nx = NA, ny = NULL, col = "grey88", lty = 1)
  lines(x, y, lwd = 2, col = col)
  abline(h = 0, col = "grey35", lwd = 1)
  if (!is.null(static_line)) {
    abline(h = static_line, col = "grey45", lwd = 1, lty = 4)
  }
  abline(v = china_relocation, col = "grey25", lwd = 1, lty = 3)
  abline(v = halving_2024, col = "grey25", lwd = 1, lty = 2)
  axis.Date(1, at = year_ticks, format = "%Y", cex.axis = 0.78)
  box()
}

draw_static_beta_legend <- function(label) {
  old_xpd <- par("xpd")
  par(xpd = NA)
  on.exit(par(xpd = old_xpd))
  legend(
    "bottom",
    inset = c(0, -0.36),
    legend = label,
    lty = 4,
    lwd = 1.2,
    col = "grey45",
    bty = "n",
    horiz = TRUE,
    cex = 0.66,
    seg.len = 1.35,
    x.intersp = 0.45
  )
}

draw_event_legend <- function() {
  plot.new()
  par(usr = c(0, 1, 0, 1))
  y <- 0.52
  cex <- 0.72
  line_len <- 0.045
  rect_w <- 0.028
  col_event <- "grey25"
  label_1 <- "China mining relocation, 2021"
  label_2 <- "April 2024 halving"
  label_3 <- "2021-2023 disruption window"

  x1 <- 0.24
  segments(x1, y, x1 + line_len, y, col = col_event, lwd = 1.2, lty = 3)
  text(x1 + line_len + 0.012, y, label_1, adj = c(0, 0.5), cex = cex)

  x2 <- 0.46
  segments(x2, y, x2 + line_len, y, col = col_event, lwd = 1.2, lty = 2)
  text(x2 + line_len + 0.012, y, label_2, adj = c(0, 0.5), cex = cex)

  x3 <- 0.64
  rect(
    x3,
    y - 0.075,
    x3 + rect_w,
    y + 0.075,
    col = adjustcolor("grey80", alpha.f = 0.55),
    border = NA
  )
  text(x3 + rect_w + 0.012, y, label_3, adj = c(0, 0.5), cex = cex)
}

draw_combined_figure <- function(output_file, device = c("png", "pdf")) {
  device <- match.arg(device)
  if (device == "png") {
    png(output_file, width = 2400, height = 2100, res = 230)
  } else {
    pdf(output_file, width = 10.2, height = 8.9, useDingbats = FALSE)
  }

  old_par <- par(no.readonly = TRUE)
  on.exit({
    par(old_par)
    dev.off()
  })

  layout(
    matrix(c(1, 2, 3, 4, 5, 6, 7, 7), nrow = 4, byrow = TRUE),
    widths = c(1, 1),
    heights = c(1, 1, 1, 0.18)
  )
  par(
    mar = c(4.35, 4.4, 1.1, 0.9),
    oma = c(2.5, 0, 4.7, 0),
    family = "serif",
    cex = 0.85
  )

  plot_panel(
    frontier,
    "beta_cost",
    expression(beta[MCI]),
    "#1b4f72",
    static_line = -0.9429
  )
  draw_static_beta_legend("Static beta = -0.943")
  mtext("Frontier ASIC-era specification", side = 3, line = 1.2, font = 2, cex = 0.9)

  plot_panel(
    weighted,
    "beta_cost",
    expression(beta[MCI]),
    "#1b4f72",
    static_line = -0.2230
  )
  draw_static_beta_legend("Static beta = -0.223")
  mtext("Weighted MCI ASIC-era specification", side = 3, line = 1.2, font = 2, cex = 0.9)

  plot_panel(frontier, "alpha_price", expression(alpha[price]), "#8e2c2c")

  plot_panel(weighted, "alpha_price", expression(alpha[price]), "#8e2c2c")

  plot_panel(frontier, "alpha_cost", expression(alpha[MCI]), "#2d6a4f")

  plot_panel(weighted, "alpha_cost", expression(alpha[MCI]), "#2d6a4f")

  par(mar = c(0, 0, 0, 0), xpd = NA)
  draw_event_legend()

  mtext("Window end date", side = 1, outer = TRUE, line = 1.35)
  mtext(
    "Figure 4.1. Rolling VECM coefficients, frontier and weighted MCI specifications",
    side = 3,
    outer = TRUE,
    line = 3.35,
    font = 2
  )
}

combined_png <- file.path(FIG_DIR, "rolling_vecm_combined_frontier_weighted_r.png")
combined_pdf <- file.path(FIG_DIR, "rolling_vecm_combined_frontier_weighted_r.pdf")

draw_combined_figure(combined_png, "png")
draw_combined_figure(combined_pdf, "pdf")

cat("Created combined figure files:\n")
cat("- ", combined_png, "\n", sep = "")
cat("- ", combined_pdf, "\n", sep = "")
cat("Frontier rows plotted: ", nrow(frontier), "\n", sep = "")
cat("Weighted rows plotted: ", nrow(weighted), "\n", sep = "")
