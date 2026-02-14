from ai_stock_analyst.agents.base import AnalysisResult
from ai_stock_analyst.agents.portfolio import PortfolioManager


def _result(name: str, signal: str, confidence: float = 0.7):
    return AnalysisResult(
        agent_name=name,
        signal=signal,
        confidence=confidence,
        reasoning="test",
        indicators={},
        risks=[],
    )


def test_buy_signal_is_downgraded_when_risk_triggered():
    manager = PortfolioManager()
    analyses = [
        _result("TechnicalAnalyst", "BUY", 0.8),
        _result("NewsAnalyst", "BUY", 0.7),
        _result("SocialMediaAnalyst", "HOLD", 0.5),
        _result("RiskManager", "HOLD", 0.8),
    ]

    result = manager.analyze(
        {
            "symbol": "AAPL",
            "analyses": analyses,
            "price_data": {"current_price": 100, "atr_pct": 5.0},
            "risk_assessment": {
                "triggered": True,
                "risk_level": "HIGH",
                "triggers": ["ATR波动偏高(5.00%)"],
                "max_position_size": "2%",
            },
        }
    )

    assert result.signal == "HOLD"
    assert result.indicators["risk_override"] is True
    assert result.indicators["position_size"] == "2%"


def test_buy_signal_kept_without_risk_triggered():
    manager = PortfolioManager()
    analyses = [
        _result("TechnicalAnalyst", "BUY", 0.8),
        _result("NewsAnalyst", "BUY", 0.7),
        _result("SocialMediaAnalyst", "SELL", 0.5),
    ]

    result = manager.analyze(
        {
            "symbol": "AAPL",
            "analyses": analyses,
            "price_data": {"current_price": 100, "atr_pct": 1.2},
            "risk_assessment": {
                "triggered": False,
                "risk_level": "LOW",
                "triggers": [],
                "max_position_size": "10%",
            },
        }
    )

    assert result.signal == "BUY"
    assert result.indicators["risk_override"] is False
