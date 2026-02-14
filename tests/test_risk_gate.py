from ai_stock_analyst.agents.base import AnalysisResult
from ai_stock_analyst.agents.portfolio import PortfolioManager
from ai_stock_analyst.agents.risk_manager import RiskManager


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


def test_geopolitical_and_trump_headlines_raise_risk():
    risk_manager = RiskManager()
    result = risk_manager.analyze(
        {
            "price_data": {
                "atr_pct": 1.5,
                "volatility_20d": 1.2,
                "change_percent": 0.8,
                "data_quality": 1.0,
            },
            "news": [
                {"title": "Trump signals new tariff policy and trade war stance"},
                {"title": "Geopolitical risk rises amid Middle East shipping disruption"},
            ],
            "social_data": {"sentiment": {"bearish_pct": 55}},
        }
    )

    assert result.indicators["geopolitics_risk_score"] >= 2
    assert result.indicators["triggered"] is True


def test_qqq_and_vix_risk_trigger():
    risk_manager = RiskManager()
    result = risk_manager.analyze(
        {
            "price_data": {
                "atr_pct": 1.0,
                "volatility_20d": 1.1,
                "change_percent": 0.5,
                "data_quality": 1.0,
                "market_context": {
                    "qqq_risk": "HIGH",
                    "qqq_ret_5d": -3.4,
                    "vix_risk": "MEDIUM",
                    "vix_level": 22.8,
                },
            },
            "news": [],
            "social_data": {"sentiment": {"bearish_pct": 48}},
        }
    )
    assert result.indicators["triggered"] is True
    assert result.indicators["qqq_risk"] == "HIGH"
