# Pre-registered Model Specification

## Research question

Does applying volatility-targeted position sizing to a simple long/cash time-series momentum strategy produce more stable risk and smaller downside losses than unscaled momentum after estimated transaction costs?

Buy and hold is included as an additional benchmark.

## Hypotheses

### Primary hypothesis

Because volatility tends to persist, scaling exposure down when estimated volatility is high and up when it is low may stabilise realised risk and reduce severe losses.

### Competing hypothesis

Volatility targeting may fail to improve risk-adjusted performance because volatility estimates are imperfect, the strategy can remain underexposed during sharp recoveries, low-volatility periods can precede losses, leverage magnifies errors, and resizing creates transaction costs.

## Initial parameters

These choices are fixed before inspecting strategy results.

| Component | Day 1 specification |
| --- | --- |
| Primary asset | SPY |
| Sample | 2007-01-01 to 2025-12-31 |
| Frequency | Daily |
| Price field | Adjusted price |
| Return type | Simple return |
| Momentum lookback | 252 trading days |
| Momentum position | Long if trailing return is positive; cash otherwise |
| Volatility window | 21 trading days |
| Annualisation factor | 252 trading days |
| Volatility target | 10% annualised |
| Maximum exposure | 1.5 |
| Rebalancing | Daily |
| Transaction cost | 10 basis points per unit of turnover |
| Day 1 cash return | Zero |

## Timing convention

The simple close-to-close return for day `t` is

```text
r[t] = P[t] / P[t-1] - 1
```

The position earning `r[t]` must be determined using information available no later than the close of day `t-1`. A signal or volatility estimate calculated using day `t` data and then applied to `r[t]` would introduce look-ahead bias.

## Strategy definitions

### Momentum signal

```text
momentum[t] = P[t] / P[t-252] - 1
signal[t] = 1 if momentum[t] > 0 else 0
```

The implementable signal is lagged by one trading day.

### Volatility estimate

```text
estimated_vol[t] = rolling_std_21(daily_returns) * sqrt(252)
```

The implementable volatility estimate is lagged by one trading day.

### Target exposure

```text
raw_weight[t] = signal[t] * 0.10 / estimated_vol[t]
weight[t] = min(1.5, raw_weight[t])
```

### Turnover and transaction costs

```text
turnover[t] = abs(weight[t] - weight[t-1])
cost[t] = 0.001 * turnover[t]
net_return[t] = weight[t] * asset_return[t] - cost[t]
```

## Required Day 1 outputs

- Clean price and return data.
- Buy-and-hold return series.
- Unscaled momentum return series.
- Gross volatility-targeted return series.
- Net volatility-targeted return series.
- Cumulative wealth, drawdown, rolling volatility and exposure charts.
- Preliminary performance table.
- Explicit sanity checks for timing, missing observations, leverage and costs.

## Day 2 robustness plan

- Replicate across TLT, GLD and DBC.
- Compare alternative volatility windows and momentum horizons.
- Compare transaction-cost assumptions.
- Examine crisis and non-crisis subperiods.
- Add a cash-rate treatment or document its effect.
- Refactor into reusable functions and automated tests.

