"""
风险管理 Agent
"""
from typing import Dict, List

from ai_stock_analyst.agents.base import AnalysisResult, BaseAgent


class RiskManager(BaseAgent):
    def __init__(self):
        super().__init__("RiskManager")

    def analyze(self, data: Dict) -> AnalysisResult:
        price_data = data.get("price_data", {})
        news_items = data.get("news", [])
        social_data = data.get("social_data", {})

        triggers: List[str] = []

        atr_pct = float(price_data.get("atr_pct", 0) or 0)
        volatility_20d = float(price_data.get("volatility_20d", 0) or 0)
        change_percent = abs(float(price_data.get("change_percent", 0) or 0))
        data_quality = float(price_data.get("data_quality", 0) or 0)

        bearish_pct = float(social_data.get("sentiment", {}).get("bearish_pct", 50) or 50)

        if atr_pct >= 4.0:
            triggers.append(f"ATR波动偏高({atr_pct:.2f}%)")
        if volatility_20d >= 3.0:
            triggers.append(f"20日波动率偏高({volatility_20d:.2f}%)")
        if change_percent >= 6.0:
            triggers.append(f"单日波动过大({change_percent:.2f}%)")
        if data_quality < 0.7:
            triggers.append(f"数据质量不足({data_quality:.2f})")
        if bearish_pct >= 70:
            triggers.append(f"社媒看空比例过高({bearish_pct:.1f}%)")

        event_keywords = ["earnings", "fomc", "cpi", "fed", "财报", "利率决议"]
        joined_titles = " ".join(item.get("title", "").lower() for item in news_items[:10])
        if any(keyword in joined_titles for keyword in event_keywords):
            triggers.append("检测到重大事件窗口")

        geopolitics_score, geopolitics_hits = self._assess_geopolitical_risk(news_items)
        if geopolitics_score >= 2:
            triggers.append(f"地缘政治风险升温({geopolitics_score})")
        if geopolitics_hits:
            triggers.append("地缘政治关键词: " + ", ".join(geopolitics_hits[:4]))

        level = "LOW"
        if len(triggers) >= 3:
            level = "HIGH"
        elif len(triggers) >= 1:
            level = "MEDIUM"

        max_position_size = "10%"
        if level == "MEDIUM":
            max_position_size = "5%"
        elif level == "HIGH":
            max_position_size = "2%"

        triggered = level != "LOW"
        signal = "HOLD" if triggered else "BUY"
        confidence = 0.78 if triggered else 0.6

        if triggered:
            reasoning = "风险闸门触发: " + "；".join(triggers)
        else:
            reasoning = "未触发重大风险闸门，可按常规仓位执行。"

        return AnalysisResult(
            agent_name=self.name,
            signal=signal,
            confidence=confidence,
            reasoning=reasoning,
            indicators={
                "triggered": triggered,
                "risk_level": level,
                "triggers": triggers,
                "max_position_size": max_position_size,
                "geopolitics_risk_score": geopolitics_score,
                "geopolitics_hits": geopolitics_hits,
            },
            risks=triggers,
        )

    def _assess_geopolitical_risk(self, news_items):
        titles = " ".join(item.get("title", "").lower() for item in news_items[:20])
        weighted_terms = {
            "trump": 1,
            "tariff": 2,
            "trade war": 2,
            "sanction": 2,
            "middle east": 2,
            "iran": 1,
            "china": 1,
            "taiwan": 2,
            "ukraine": 2,
            "russia": 1,
            "geopolitical": 2,
            "shipping disruption": 2,
        }
        hits = []
        score = 0
        for term, weight in weighted_terms.items():
            if term in titles:
                hits.append(term)
                score += weight
        return score, hits
