# Risk-Controlled Momentum

An empirical Python project investigating whether volatility-targeted position sizing makes a simple time-series momentum strategy's risk more stable and reduces downside losses after estimated transaction costs.

## Research question

Does applying volatility-targeted exposure to a long/cash time-series momentum strategy produce more stable realised risk and smaller downside losses than unscaled momentum after transaction costs?

## Day 1 status

Day 1 computational implementation is complete under the unchanged specification in [`docs/model_spec.md`](docs/model_spec.md). All eleven sections of [`notebooks/01_prototype.ipynb`](notebooks/01_prototype.ipynb) run from top to bottom in a clean kernel, with 89 of 89 consolidated checks passing. The notebook regenerates the preliminary performance table, validation record and four-panel figure. The sample results show lower realised volatility and maximum drawdown for net volatility targeting than unscaled momentum, alongside lower compound return. These descriptive results are not evidence of guaranteed future performance.

## Day 2 status

Day 2 refactoring has started without changing the locked model. The simple-return calculation now lives in a reusable project package, is called by the notebook and is covered by focused automated tests for the formula, index alignment and missing-price behaviour.

## Initial comparison

1. Buy and hold.
2. Unscaled long/cash time-series momentum.
3. Volatility-targeted time-series momentum before costs.
4. Volatility-targeted time-series momentum after costs.

## Repository structure

```text
volatility-targeted-momentum/
├── README.md
├── pyproject.toml
├── requirements.txt
├── volatility_targeted_momentum/
│   └── core.py
├── tests/
│   └── test_core.py
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

## Environment and tests

From the repository root, install the declared environment and run the automated tests:

```text
python -m pip install -r requirements.txt
python -m pytest -q
```

## Important limitation

This is an educational empirical-research project, not investment advice or a claim of a profitable trading strategy.
