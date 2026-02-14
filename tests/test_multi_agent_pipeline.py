from ai_stock_analyst.agents.analyzer import StockAnalyzer


def test_pipeline_contains_new_roles_and_risk():
    analyzer = StockAnalyzer()
    keys = analyzer.list_agents()
    assert "fundamental" in keys
    assert "bull" in keys
    assert "bear" in keys
    assert "risk" in keys


def test_analysis_has_risk_payload_and_decision_fields():
    analyzer = StockAnalyzer()
    data = {
        "symbol": "AAPL",
        "price_data": {
            "current_price": 100,
            "previous_close": 98,
            "change_percent": 2,
            "ma5": 100,
            "ma20": 98,
            "trend": "BULLISH",
            "rsi14": 60,
            "macd": 1.2,
            "macd_signal": 1.0,
            "macd_hist": 0.2,
            "atr_pct": 2.1,
            "volatility_20d": 1.5,
            "data_quality": 1.0,
            "history": None,
        },
        "news": [{"title": "AAPL earnings beat estimates", "source": "Test"}],
        "social_data": {"sentiment": {"bullish_pct": 60, "bearish_pct": 40}, "total": 10},
    }

    result = analyzer.analyze("AAPL", data)
    assert "decision" in result
    assert "position_size" in result["decision"]
    assert any(a["agent"] == "RiskManager" for a in result["analyses"])
