# Data

The prototype downloads adjusted daily market prices programmatically. Locally cached data belongs in `data/cache/` and is not committed by default.

## Day 1 SPY pipeline

| Item | Recorded value |
| --- | --- |
| Provider | Yahoo Finance, accessed through `yfinance` |
| Library version | `yfinance 1.6.0` |
| Download date | 2026-08-21 |
| Ticker | SPY |
| Interval | Daily |
| Locked sample | 2007-01-01 to 2025-12-31 |
| API request boundary | `start="2007-01-01"`, `end="2026-01-01"` |
| Adjustment | `auto_adjust=True` |
| Selected field | Adjusted `Close`, renamed `adjusted_price` |
| Observations returned | 4,780 |
| First observation | 2007-01-03 |
| Last observation | 2025-12-31 |
| Missing selected prices | 0 |

The API's start boundary is inclusive and its end boundary is exclusive. The request therefore uses `2026-01-01` to include data through the locked sample end of `2025-12-31`. The first observation is the first available trading day within the sample, not necessarily the calendar start date.

With `auto_adjust=True`, installed `yfinance 1.6.0` adjusts the OHLC columns and returns no separate `Adj Close` column. The pipeline explicitly selects `Close` under that adjustment setting.

## Validation

The notebook stops if the download is empty or lacks `Close`. It then checks that the selected series has a datetime index, increasing and unique dates, no missing values, strictly positive prices and coverage within both ends of the locked sample. A seven-calendar-day boundary tolerance accommodates weekends and exchange holidays without changing the research sample.

No missing selected prices were imputed or forward-filled. No local data cache was written at this checkpoint.

During the return-series validation run, one live request returned no observations. The notebook's empty-download guard stopped execution, and an unchanged retry returned the complete validated sample. Live acquisition can therefore fail transiently; an empty response must never be treated as a valid dataset or silently carried into calculations.

## Known limitations

- Yahoo Finance is an external data provider and can revise historical observations or change its interface.
- Adjusted daily closes do not represent intraday execution prices, bid-ask spreads or market impact.
- The adjustment depends on the provider's corporate-action data.
- The observation count can change if the provider corrects its history; the validation rules matter more than a permanently hard-coded row count.
