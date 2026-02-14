"""
宏观环境 Agent
"""
from __future__ import annotations

from typing import Dict, List

from ai_stock_analyst.agents.base import AnalysisResult, BaseAgent


class MacroRegimeAgent(BaseAgent):
    """评估大盘风险偏好与宏观事件冲击。"""

    def __init__(self):
        super().__init__("MacroRegimeAgent")

    def analyze(self, data: Dict) -> AnalysisResult:
        price_data = data.get("price_data", {}) or {}
        market_context = price_data.get("market_context", {}) or {}
        news_items = data.get("news", []) or []

        qqq_risk = str(market_context.get("qqq_risk", "LOW")).upper()
        vix_risk = str(market_context.get("vix_risk", "LOW")).upper()
        qqq_ret_5d = float(market_context.get("qqq_ret_5d", 0) or 0)
        vix_level = float(market_context.get("vix_level", 0) or 0)

        score = 0
        reasons: List[str] = []

        if qqq_risk == "LOW":
            score += 1
            reasons.append(f"纳指ETF风险较低(5日{qqq_ret_5d:.2f}%)")
        elif qqq_risk == "MEDIUM":
            score -= 1
            reasons.append(f"纳指ETF风险中等(5日{qqq_ret_5d:.2f}%)")
        elif qqq_risk == "HIGH":
            score -= 2
            reasons.append(f"纳指ETF风险较高(5日{qqq_ret_5d:.2f}%)")

        if vix_risk == "LOW":
            score += 1
            reasons.append(f"VIX处于低位({vix_level:.2f})")
        elif vix_risk == "MEDIUM":
            score -= 1
            reasons.append(f"VIX处于中位({vix_level:.2f})")
        elif vix_risk == "HIGH":
            score -= 2
            reasons.append(f"VIX偏高({vix_level:.2f})")

        joined_titles = " ".join(item.get("title", "").lower() for item in news_items[:12])
        risk_keywords = [
            "trump", "tariff", "sanction", "trade war", "geopolitical", "middle east",
            "ukraine", "russia", "taiwan", "shipping disruption", "hawkish", "hot inflation",
        ]
        positive_keywords = [
            "cooling inflation", "rate cut", "fed pause", "soft landing",
            "stimulus", "政策宽松", "通胀回落",
        ]
        risk_hits = [k for k in risk_keywords if k in joined_titles]
        pos_hits = [k for k in positive_keywords if k in joined_titles]

        if risk_hits:
            score -= min(len(risk_hits), 3)
            reasons.append(f"宏观/政策风险关键词: {', '.join(risk_hits[:3])}")
        if pos_hits:
            score += min(len(pos_hits), 2)
            reasons.append(f"宏观偏正面关键词: {', '.join(pos_hits[:2])}")

        if score >= 2:
            signal = "BUY"
        elif score <= -2:
            signal = "SELL"
        else:
            signal = "HOLD"

        confidence = min(0.85, 0.45 + abs(score) * 0.1)
        reasoning = "\n".join(f"- {line}" for line in reasons) if reasons else "- 宏观信息不足，维持中性。"

        return AnalysisResult(
            agent_name=self.name,
            signal=signal,
            confidence=confidence,
            reasoning=reasoning,
            indicators={
                "macro_score": score,
                "qqq_risk": qqq_risk,
                "vix_risk": vix_risk,
                "qqq_ret_5d": qqq_ret_5d,
                "vix_level": vix_level,
                "risk_keywords": risk_hits[:5],
                "positive_keywords": pos_hits[:5],
            },
            risks=risk_hits[:3],
        )
