"""Core calculations shared by the research notebook and automated tests."""

from __future__ import annotations

import pandas as pd


def calculate_simple_returns(adjusted_prices: pd.Series) -> pd.Series:
    """Calculate unfilled close-to-close simple returns from adjusted prices."""

    return adjusted_prices.pct_change(fill_method=None).rename("asset_return")


def calculate_momentum_signals(
    adjusted_prices: pd.Series,
    lookback_days: int,
    timing_lag_days: int,
) -> pd.DataFrame:
    """Calculate trailing momentum, its raw signal and the lagged position."""

    trailing_momentum = adjusted_prices.pct_change(
        periods=lookback_days,
        fill_method=None,
    ).rename("trailing_momentum")
    raw_momentum_signal = (
        trailing_momentum.gt(0).astype(float).where(trailing_momentum.notna())
    ).rename("raw_momentum_signal")
    momentum_position = raw_momentum_signal.shift(timing_lag_days).rename(
        "momentum_position"
    )

    return pd.concat(
        [trailing_momentum, raw_momentum_signal, momentum_position],
        axis=1,
    )
