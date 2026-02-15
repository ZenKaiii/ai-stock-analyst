from ai_stock_analyst.agents.recommendation import (
    _calc_fundamental_score,
    _calc_news_sentiment,
    _calc_source_quality,
    _calc_technical_score,
    _normalize_prefilter_score,
)


def test_normalize_prefilter_score_bounds():
    assert 0.0 <= _normalize_prefilter_score(-100) <= 1.0
    assert 0.0 <= _normalize_prefilter_score(100) <= 1.0


def test_news_sentiment_defaults_neutral():
    assert _calc_news_sentiment([]) == 0.5


def test_technical_score_higher_for_bullish_setup():
    bullish = _calc_technical_score({"trend": "BULLISH", "rsi14": 58, "macd_hist": 0.3, "atr_pct": 2.0})
    weak = _calc_technical_score({"trend": "BEARISH", "rsi14": 30, "macd_hist": -0.2, "atr_pct": 7.0})
    assert bullish > weak


def test_fundamental_score_higher_for_growth_balance_sheet():
    strong = _calc_fundamental_score(
        {
            "revenue_growth": 0.12,
            "earnings_growth": 0.15,
            "profit_margins": 0.2,
            "return_on_equity": 0.18,
            "debt_to_equity": 60,
            "pe_ratio": 30,
        }
    )
    weak = _calc_fundamental_score(
        {
            "revenue_growth": -0.05,
            "earnings_growth": -0.1,
            "profit_margins": 0.03,
            "return_on_equity": 0.04,
            "debt_to_equity": 280,
            "pe_ratio": 120,
        }
    )
    assert strong > weak


def test_source_quality_prefers_high_quality_diversified_sources():
    high_quality = _calc_source_quality(
        [
            {"source": "WSJ"},
            {"source": "SEC Press Releases"},
            {"source": "Federal Reserve"},
        ]
    )
    low_quality = _calc_source_quality(
        [
            {"source": "Unknown Blog"},
            {"source": "Unknown Blog"},
        ]
    )
    assert high_quality > low_quality
