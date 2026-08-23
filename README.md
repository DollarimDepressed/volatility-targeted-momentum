# Risk-Controlled Momentum

An empirical Python project investigating whether volatility-targeted position sizing makes a simple time-series momentum strategy's risk more stable and reduces downside losses after estimated transaction costs.

## Research question

Does applying volatility-targeted exposure to a long/cash time-series momentum strategy produce more stable realised risk and smaller downside losses than unscaled momentum after transaction costs?

## Day 1 status

The initial specification remains locked in [`docs/model_spec.md`](docs/model_spec.md). Sections 1–8 of [`notebooks/01_prototype.ipynb`](notebooks/01_prototype.ipynb) now validate adjusted SPY prices and returns, build buy and hold, construct lagged momentum and volatility estimates, calculate capped volatility-targeted gross returns, and deduct estimated transaction costs using daily turnover. Comparative wealth paths and performance metrics are the next Day 1 checkpoint.

## Initial comparison

1. Buy and hold.
2. Unscaled long/cash time-series momentum.
3. Volatility-targeted time-series momentum before costs.
4. Volatility-targeted time-series momentum after costs.

## Repository structure

```text
volatility-targeted-momentum/
├── README.md
├── requirements.txt
├── docs/
│   └── model_spec.md
├── notebooks/
│   └── 01_prototype.ipynb
├── data/
│   └── README.md
└── outputs/
    ├── figures/
    └── tables/
```

## Important limitation

This is an educational empirical-research project, not investment advice or a claim of a profitable trading strategy.
