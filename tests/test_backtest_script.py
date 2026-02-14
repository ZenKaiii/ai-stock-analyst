import pandas as pd

from scripts.backtest_strategy import _extract_close_series, _normalize_ohlcv


def test_extract_close_series_handles_multiindex():
    idx = pd.date_range("2025-01-01", periods=3)
    cols = pd.MultiIndex.from_product([["Close", "Open"], ["SPY"]])
    df = pd.DataFrame([[100, 99], [101, 100], [102, 101]], index=idx, columns=cols)

    close = _extract_close_series(df)
    assert len(close) == 3
    assert float(close.iloc[-1]) == 102.0


def test_normalize_ohlcv_handles_multiindex():
    idx = pd.date_range("2025-01-01", periods=3)
    cols = pd.MultiIndex.from_product([["Open", "High", "Low", "Close", "Volume"], ["SPY"]])
    df = pd.DataFrame(
        [[99, 101, 98, 100, 10], [100, 102, 99, 101, 11], [101, 103, 100, 102, 12]],
        index=idx,
        columns=cols,
    )

    out = _normalize_ohlcv(df)
    assert list(out.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert float(out["Close"].iloc[-1]) == 102.0
