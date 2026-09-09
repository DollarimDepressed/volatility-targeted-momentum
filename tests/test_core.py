import numpy as np
import pandas as pd

from volatility_targeted_momentum import (
    calculate_momentum_signals,
    calculate_simple_returns,
    calculate_target_exposure,
    calculate_turnover_and_costs,
    calculate_volatility_estimates,
)


def test_simple_returns_match_manual_formula() -> None:
    dates = pd.date_range("2026-01-01", periods=3, freq="D")
    prices = pd.Series([100.0, 102.0, 101.0], index=dates, name="adjusted_price")
    expected = pd.Series(
        [np.nan, 102.0 / 100.0 - 1.0, 101.0 / 102.0 - 1.0],
        index=dates,
        name="asset_return",
    )

    actual = calculate_simple_returns(prices)

    pd.testing.assert_series_equal(actual, expected)


def test_simple_returns_preserve_the_price_index() -> None:
    dates = pd.to_datetime(["2026-01-02", "2026-01-05"])
    prices = pd.Series([50.0, 51.0], index=dates, name="adjusted_price")

    returns = calculate_simple_returns(prices)

    assert returns.index.equals(prices.index)
    assert returns.name == "asset_return"


def test_simple_returns_do_not_fill_missing_prices() -> None:
    dates = pd.date_range("2026-01-01", periods=3, freq="D")
    prices = pd.Series([100.0, np.nan, 102.0], index=dates, name="adjusted_price")

    returns = calculate_simple_returns(prices)

    assert returns.isna().all()


def test_momentum_signals_match_known_price_example() -> None:
    dates = pd.date_range("2026-01-01", periods=5, freq="D")
    prices = pd.Series(
        [100.0, 90.0, 80.0, 100.0, 90.0],
        index=dates,
        name="adjusted_price",
    )
    expected = pd.DataFrame(
        {
            "trailing_momentum": [
                np.nan,
                np.nan,
                80.0 / 100.0 - 1.0,
                100.0 / 90.0 - 1.0,
                90.0 / 80.0 - 1.0,
            ],
            "raw_momentum_signal": [np.nan, np.nan, 0.0, 1.0, 1.0],
            "momentum_position": [np.nan, np.nan, np.nan, 0.0, 1.0],
        },
        index=dates,
    )

    actual = calculate_momentum_signals(
        prices,
        lookback_days=2,
        timing_lag_days=1,
    )

    pd.testing.assert_frame_equal(actual, expected)


def test_momentum_warmup_remains_missing_instead_of_cash() -> None:
    prices = pd.Series([100.0, 90.0, 80.0, 100.0, 90.0])

    result = calculate_momentum_signals(
        prices,
        lookback_days=2,
        timing_lag_days=1,
    )

    assert result["raw_momentum_signal"].iloc[:2].isna().all()
    assert result["momentum_position"].iloc[:3].isna().all()


def test_momentum_position_equals_the_lagged_raw_signal() -> None:
    prices = pd.Series([100.0, 90.0, 80.0, 100.0, 90.0])
    timing_lag_days = 1

    result = calculate_momentum_signals(
        prices,
        lookback_days=2,
        timing_lag_days=timing_lag_days,
    )
    expected_position = result["raw_momentum_signal"].shift(
        timing_lag_days
    ).rename("momentum_position")

    pd.testing.assert_series_equal(
        result["momentum_position"],
        expected_position,
    )


def test_volatility_estimates_match_manual_sample_standard_deviation() -> None:
    returns = pd.Series([np.nan, 0.01, -0.01, 0.02, 0.00])
    first_window = np.array([0.01, -0.01, 0.02])
    manual_daily_volatility = np.sqrt(
        ((first_window - first_window.mean()) ** 2).sum()
        / (len(first_window) - 1)
    )

    result = calculate_volatility_estimates(
        returns,
        window_days=3,
        annualisation_days=4,
        timing_lag_days=1,
    )

    assert np.isclose(
        result["rolling_daily_volatility"].iloc[3],
        manual_daily_volatility,
    )
    assert np.isclose(
        result["raw_annualised_volatility"].iloc[3],
        manual_daily_volatility * np.sqrt(4),
    )


def test_volatility_warmup_and_lag_remain_missing() -> None:
    returns = pd.Series([np.nan, 0.01, -0.01, 0.02, 0.00])

    result = calculate_volatility_estimates(
        returns,
        window_days=3,
        annualisation_days=4,
        timing_lag_days=1,
    )

    assert result["raw_annualised_volatility"].iloc[:3].isna().all()
    assert result["lagged_volatility_estimate"].iloc[:4].isna().all()


def test_lagged_volatility_equals_the_previous_raw_estimate() -> None:
    returns = pd.Series([np.nan, 0.01, -0.01, 0.02, 0.00])
    timing_lag_days = 1

    result = calculate_volatility_estimates(
        returns,
        window_days=3,
        annualisation_days=4,
        timing_lag_days=timing_lag_days,
    )
    expected = result["raw_annualised_volatility"].shift(
        timing_lag_days
    ).rename("lagged_volatility_estimate")

    pd.testing.assert_series_equal(
        result["lagged_volatility_estimate"],
        expected,
    )


def test_volatility_requires_a_complete_nonmissing_window() -> None:
    returns = pd.Series([0.01, -0.01, np.nan, 0.02, 0.01, 0.00])

    result = calculate_volatility_estimates(
        returns,
        window_days=3,
        annualisation_days=4,
        timing_lag_days=1,
    )

    assert result["raw_annualised_volatility"].first_valid_index() == 5


def make_exposure_example() -> tuple[pd.Series, pd.Series, pd.Series]:
    dates = pd.date_range("2026-01-01", periods=5, freq="D")
    positions = pd.Series(
        [np.nan, 0.0, 1.0, 1.0, 1.0],
        index=dates,
        name="momentum_position",
    )
    volatility = pd.Series(
        [np.nan, 0.20, 0.20, 0.08, 0.04],
        index=dates,
        name="lagged_volatility_estimate",
    )
    returns = pd.Series(
        [np.nan, 0.01, 0.02, -0.03, 0.04],
        index=dates,
        name="asset_return",
    )
    return positions, volatility, returns


def test_target_exposure_matches_known_example() -> None:
    positions, volatility, returns = make_exposure_example()
    expected = pd.DataFrame(
        {
            "volatility_scalar": [np.nan, 0.50, 0.50, 1.25, 2.50],
            "raw_target_exposure": [np.nan, 0.00, 0.50, 1.25, 2.50],
            "target_exposure": [np.nan, 0.00, 0.50, 1.25, 1.50],
            "gross_vol_targeted_return": [
                np.nan,
                0.00,
                0.01,
                -0.0375,
                0.06,
            ],
        },
        index=positions.index,
    )

    actual = calculate_target_exposure(
        positions,
        volatility,
        returns,
        target_volatility=0.10,
        maximum_exposure=1.50,
    )

    pd.testing.assert_frame_equal(actual, expected)


def test_cash_position_blocks_volatility_scaled_exposure() -> None:
    positions, volatility, returns = make_exposure_example()

    result = calculate_target_exposure(
        positions,
        volatility,
        returns,
        target_volatility=0.10,
        maximum_exposure=1.50,
    )

    assert np.isclose(result["volatility_scalar"].iloc[1], 0.50)
    assert np.isclose(result["target_exposure"].iloc[1], 0.00)


def test_target_exposure_respects_the_leverage_cap() -> None:
    positions, volatility, returns = make_exposure_example()

    result = calculate_target_exposure(
        positions,
        volatility,
        returns,
        target_volatility=0.10,
        maximum_exposure=1.50,
    )

    assert np.isclose(result["raw_target_exposure"].iloc[-1], 2.50)
    assert np.isclose(result["target_exposure"].iloc[-1], 1.50)
    assert result["target_exposure"].dropna().le(1.50).all()


def test_gross_return_equals_exposure_times_asset_return() -> None:
    positions, volatility, returns = make_exposure_example()

    result = calculate_target_exposure(
        positions,
        volatility,
        returns,
        target_volatility=0.10,
        maximum_exposure=1.50,
    )
    expected = (
        result["target_exposure"] * returns
    ).rename("gross_vol_targeted_return")

    pd.testing.assert_series_equal(
        result["gross_vol_targeted_return"],
        expected,
    )


def make_cost_example() -> tuple[pd.Series, pd.Series]:
    dates = pd.date_range("2026-01-01", periods=6, freq="D")
    exposure = pd.Series(
        [np.nan, 0.50, 1.10, 0.40, 0.40, 0.00],
        index=dates,
        name="target_exposure",
    )
    gross_returns = pd.Series(
        [np.nan, 0.01, -0.02, 0.00, 0.005, 0.00],
        index=dates,
        name="gross_vol_targeted_return",
    )
    return exposure, gross_returns


def test_turnover_and_costs_match_known_example() -> None:
    exposure, gross_returns = make_cost_example()
    expected = pd.DataFrame(
        {
            "previous_target_exposure": [
                np.nan,
                0.00,
                0.50,
                1.10,
                0.40,
                0.40,
            ],
            "exposure_change": [np.nan, 0.50, 0.60, -0.70, 0.00, -0.40],
            "turnover": [np.nan, 0.50, 0.60, 0.70, 0.00, 0.40],
            "estimated_transaction_cost": [
                np.nan,
                0.0005,
                0.0006,
                0.0007,
                0.0000,
                0.0004,
            ],
            "net_vol_targeted_return": [
                np.nan,
                0.0095,
                -0.0206,
                -0.0007,
                0.0050,
                -0.0004,
            ],
        },
        index=exposure.index,
    )

    actual = calculate_turnover_and_costs(
        exposure,
        gross_returns,
        transaction_cost_rate=0.001,
    )

    pd.testing.assert_frame_equal(actual, expected, check_exact=False)


def test_initial_entry_is_measured_from_cash() -> None:
    exposure, gross_returns = make_cost_example()

    result = calculate_turnover_and_costs(
        exposure,
        gross_returns,
        transaction_cost_rate=0.001,
    )
    first_exposure_date = exposure.first_valid_index()

    assert np.isclose(result.loc[first_exposure_date, "previous_target_exposure"], 0.0)
    assert np.isclose(
        result.loc[first_exposure_date, "turnover"],
        exposure.loc[first_exposure_date],
    )


def test_turnover_is_absolute_and_unchanged_exposure_costs_zero() -> None:
    exposure, gross_returns = make_cost_example()

    result = calculate_turnover_and_costs(
        exposure,
        gross_returns,
        transaction_cost_rate=0.001,
    )

    assert np.isclose(result["exposure_change"].iloc[3], -0.70)
    assert np.isclose(result["turnover"].iloc[3], 0.70)
    assert np.isclose(result["estimated_transaction_cost"].iloc[4], 0.0)


def test_exit_cost_can_make_zero_gross_return_negative_net() -> None:
    exposure, gross_returns = make_cost_example()

    result = calculate_turnover_and_costs(
        exposure,
        gross_returns,
        transaction_cost_rate=0.001,
    )

    assert np.isclose(gross_returns.iloc[-1], 0.0)
    assert np.isclose(result["estimated_transaction_cost"].iloc[-1], 0.0004)
    assert np.isclose(result["net_vol_targeted_return"].iloc[-1], -0.0004)
