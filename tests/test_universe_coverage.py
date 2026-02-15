from ai_stock_analyst.data import universe


def test_universe_includes_nyse_and_amex_and_filters_etf(monkeypatch):
    monkeypatch.setattr(
        universe,
        "_load_nasdaq_listed_rows",
        lambda: [
            {"symbol": "AAPL", "exchange": "Q", "etf": "N"},
            {"symbol": "QQQ", "exchange": "Q", "etf": "Y"},
        ],
    )
    monkeypatch.setattr(
        universe,
        "_load_other_listed_rows",
        lambda: [
            {"symbol": "JPM", "exchange": "N", "etf": "N"},
            {"symbol": "SPY", "exchange": "P", "etf": "Y"},
            {"symbol": "F", "exchange": "A", "etf": "N"},
        ],
    )

    symbols, stats = universe.load_us_equity_universe_with_stats(max_symbols=0, include_etf=False)

    assert "AAPL" in symbols
    assert "JPM" in symbols
    assert "F" in symbols
    assert "QQQ" not in symbols
    assert "SPY" not in symbols
    assert stats["exchange_breakdown"]["NASDAQ"] == 1
    assert stats["exchange_breakdown"]["NYSE"] == 1
    assert stats["exchange_breakdown"]["NYSE American"] == 1


def test_universe_cap_limit_applies_after_cleaning(monkeypatch):
    monkeypatch.setattr(
        universe,
        "_load_nasdaq_listed_rows",
        lambda: [{"symbol": "AAPL", "exchange": "Q", "etf": "N"}],
    )
    monkeypatch.setattr(
        universe,
        "_load_other_listed_rows",
        lambda: [
            {"symbol": "JPM", "exchange": "N", "etf": "N"},
            {"symbol": "MSFT", "exchange": "Q", "etf": "N"},
        ],
    )

    symbols, stats = universe.load_us_equity_universe_with_stats(max_symbols=2, include_etf=False)

    assert len(symbols) == 2
    assert stats["selected_universe"] == 2
