from ai_stock_analyst.agents.recommendation import KNOWN_TICKERS, RecommendationAgent


def test_recommendation_agent_supports_top21_and_plain_markdown(monkeypatch):
    agent = RecommendationAgent()

    def _identity_enrich(stock_signals):
        for _, data in stock_signals.items():
            data["composite_score"] = data.get("bullish_score", 0.5)
            data["brief_analysis"] = "趋势中性，等待确认。"
            data["recommend_reason"] = "仅用于回退路径验证。"
            data["evidence_news"] = ["[测试源] 事件：测试；解读：测试"]
            data["company_name"] = data.get("company_name", "TestCo")
            data["sector"] = "科技"
            data["industry"] = "软件"
            data["business"] = "测试业务"
        return stock_signals

    monkeypatch.setattr(agent, "_enrich_with_market_quality", _identity_enrich)

    tickers = sorted(KNOWN_TICKERS)[:24]
    all_news = [{"title": f"{t} upgrade growth outlook", "source": "TestSource", "summary": "positive"} for t in tickers]
    result = agent.analyze({"all_news": all_news, "top_k": 21})

    assert len(result.indicators["top_picks"]) == 21
    assert "**" not in result.reasoning
    assert "`" not in result.reasoning
