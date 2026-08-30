import numpy as np
import pandas as pd

from volatility_targeted_momentum import calculate_simple_returns


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
