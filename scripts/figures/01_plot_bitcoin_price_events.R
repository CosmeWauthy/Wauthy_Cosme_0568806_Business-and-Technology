#!/usr/bin/env Rscript

# Descriptive Bitcoin price figure with halving and mining-technology events.

ROOT <- Sys.getenv("THESIS_ANALYSIS_ROOT", unset = getwd())
RAW_PRICE_PATH <- file.path(ROOT, "data/raw/bitcoinity_data_price.csv")
PANEL_PATH <- file.path(ROOT, "data/processed/monthly/monthly_master_panel.csv")
FIG_DIR <- file.path(ROOT, "outputs/figures")
OUTPUT_FILE <- file.path(FIG_DIR, "bitcoin_price_timeseries_events.png")

dir.create(FIG_DIR, recursive = TRUE, showWarnings = FALSE)

load_price_series <- function() {
  if (file.exists(RAW_PRICE_PATH)) {
    btc <- read.csv(RAW_PRICE_PATH, stringsAsFactors = FALSE, check.names = FALSE)
    exchange_cols <- setdiff(names(btc), "Time")
    btc$Date <- as.Date(sub(" .*", "", btc$Time))
    btc$price_usd <- rowMeans(btc[exchange_cols], na.rm = TRUE)
    btc$price_usd[!is.finite(btc$price_usd)] <- NA_real_
    btc <- btc[!is.na(btc$price_usd), c("Date", "price_usd")]
    return(btc)
  }

  panel <- read.csv(PANEL_PATH, stringsAsFactors = FALSE)
  data.frame(
    Date = as.Date(panel$month),
    price_usd = panel$bitcoin_market_price_usd
  )
}

btc <- load_price_series()

events <- data.frame(
  date = as.Date(c(
    "2012-11-28",
    "2013-01-31",
    "2016-05-31",
    "2016-07-09",
    "2020-05-11",
    "2021-05-21",
    "2021-06-18",
    "2024-04-19"
  )),
  label = c(
    "First halving",
    "Avalon S1 released",
    "Antminer S9 released",
    "Second halving",
    "Third halving",
    "China mining crackdown",
    "Sichuan shutdown",
    "Fourth halving"
  ),
  stringsAsFactors = FALSE
)

events$y <- approx(
  x = btc$Date,
  y = btc$price_usd,
  xout = events$date,
  rule = 2
)$y

events$pch <- c(0, 1, 2, 5, 6, 15, 16, 17)
events$color <- c(
  "#1b9e77",
  "#d95f02",
  "#7570b3",
  "#e7298a",
  "#66a61e",
  "#e6ab02",
  "#a6761d",
  "#1f78b4"
)

png(OUTPUT_FILE, width = 1800, height = 1000, res = 180)

par(mar = c(5, 5, 4, 2) + 0.1, oma = c(0, 0, 2, 0))
plot(
  btc$Date,
  btc$price_usd,
  type = "l",
  col = "black",
  lwd = 2,
  xlab = "Date",
  ylab = "Bitcoin price (USD)",
  main = ""
)

for (i in seq_len(nrow(events))) {
  points(
    x = events$date[i],
    y = events$y[i],
    pch = events$pch[i],
    cex = 1.3,
    lwd = 1.4,
    col = events$color[i],
    bg = events$color[i]
  )
}

legend(
  "topleft",
  legend = c(
    "Bitcoin price series",
    "2012-11-28 First halving",
    "2013-01-31 Avalon S1 released",
    "2016-05-31 Antminer S9 released",
    "2016-07-09 Second halving",
    "2020-05-11 Third halving",
    "2021-05-21 China mining crackdown",
    "2021-06-18 Sichuan shutdown",
    "2024-04-19 Fourth halving"
  ),
  col = c("black", events$color),
  lty = c(1, rep(NA, 8)),
  lwd = c(2, rep(NA, 8)),
  pch = c(NA, events$pch),
  pt.cex = c(NA, rep(1.1, 8)),
  bty = "n",
  cex = 0.8,
  y.intersp = 1.05
)

mtext(
  "Bitcoin Price Time Series with Mining and Halving Events",
  side = 3,
  outer = TRUE,
  line = 0.5,
  cex = 1.3,
  font = 2
)

dev.off()

cat("Saved plot to: ", OUTPUT_FILE, "\n", sep = "")
