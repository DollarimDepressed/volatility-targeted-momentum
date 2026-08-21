# Risk-Controlled Momentum

An empirical Python project investigating whether volatility-targeted position sizing makes a simple time-series momentum strategy's risk more stable and reduces downside losses after estimated transaction costs.

## Research question

Does applying volatility-targeted exposure to a long/cash time-series momentum strategy produce more stable realised risk and smaller downside losses than unscaled momentum after transaction costs?

## Day 1 status

The initial specification remains locked in [`docs/model_spec.md`](docs/model_spec.md). Sections 1–2 of [`notebooks/01_prototype.ipynb`](notebooks/01_prototype.ipynb) now define the locked configuration and download and validate the adjusted SPY price series. No return or strategy result has yet been calculated.

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
