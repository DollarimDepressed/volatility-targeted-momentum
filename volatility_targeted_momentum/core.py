"""Core calculations shared by the research notebook and automated tests."""

from __future__ import annotations

import numpy as np
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


def calculate_volatility_estimates(
    asset_returns: pd.Series,
    window_days: int,
    annualisation_days: int,
    timing_lag_days: int,
) -> pd.DataFrame:
    """Calculate rolling, annualised and implementable volatility estimates."""

    rolling_daily_volatility = (
        asset_returns.rolling(window=window_days, min_periods=window_days)
        .std(ddof=1)
        .rename("rolling_daily_volatility")
    )
    raw_annualised_volatility = (
        rolling_daily_volatility * np.sqrt(annualisation_days)
    ).rename("raw_annualised_volatility")
    lagged_volatility_estimate = raw_annualised_volatility.shift(
        timing_lag_days
    ).rename("lagged_volatility_estimate")

    return pd.concat(
        [
            rolling_daily_volatility,
            raw_annualised_volatility,
            lagged_volatility_estimate,
        ],
        axis=1,
    )


def calculate_target_exposure(
    momentum_position: pd.Series,
    lagged_volatility_estimate: pd.Series,
    asset_returns: pd.Series,
    target_volatility: float,
    maximum_exposure: float,
) -> pd.DataFrame:
    """Calculate scaled exposure, apply its cap and calculate gross returns."""

    volatility_scalar = (
        target_volatility / lagged_volatility_estimate
    ).rename("volatility_scalar")
    raw_target_exposure = (momentum_position * volatility_scalar).rename(
        "raw_target_exposure"
    )
    target_exposure = raw_target_exposure.clip(upper=maximum_exposure).rename(
        "target_exposure"
    )
    gross_vol_targeted_return = (target_exposure * asset_returns).rename(
        "gross_vol_targeted_return"
    )

    return pd.concat(
        [
            volatility_scalar,
            raw_target_exposure,
            target_exposure,
            gross_vol_targeted_return,
        ],
        axis=1,
    )


def calculate_turnover_and_costs(
    target_exposure: pd.Series,
    gross_strategy_returns: pd.Series,
    transaction_cost_rate: float,
) -> pd.DataFrame:
    """Calculate exposure changes, turnover, costs and net strategy returns."""

    first_exposure_date = target_exposure.first_valid_index()
    previous_target_exposure = target_exposure.shift(1).rename(
        "previous_target_exposure"
    )
    previous_target_exposure.loc[first_exposure_date] = 0.0
    exposure_change = (target_exposure - previous_target_exposure).rename(
        "exposure_change"
    )
    turnover = exposure_change.abs().rename("turnover")
    estimated_transaction_cost = (transaction_cost_rate * turnover).rename(
        "estimated_transaction_cost"
    )
    net_strategy_returns = (
        gross_strategy_returns - estimated_transaction_cost
    ).rename("net_vol_targeted_return")

    return pd.concat(
        [
            previous_target_exposure,
            exposure_change,
            turnover,
            estimated_transaction_cost,
            net_strategy_returns,
        ],
        axis=1,
    )
