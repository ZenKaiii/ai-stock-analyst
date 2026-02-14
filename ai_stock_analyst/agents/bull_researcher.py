"""
多头研究员 Agent
"""
from typing import Dict

from ai_stock_analyst.agents.base import AnalysisResult, BaseAgent


class BullResearcher(BaseAgent):
    def __init__(self):
        super().__init__("BullResearcher")

    def analyze(self, data: Dict) -> AnalysisResult:
        symbol = data.get("symbol", "")
        price_data = data.get("price_data", {})
        news_items = data.get("news", [])
        social = data.get("social_data", {}).get("sentiment", {})

        rsi14 = float(price_data.get("rsi14", 50) or 50)
        macd_hist = float(price_data.get("macd_hist", 0) or 0)
        trend = price_data.get("trend", "NEUTRAL")
        bullish_pct = float(social.get("bullish_pct", 50) or 50)

        headlines = "\n".join(f"- {n.get('title', '')}" for n in news_items[:6])
        prompt = f"""
作为多头研究员，请为 {symbol} 提供最强多头论据：
RSI14={rsi14}, MACD_HIST={macd_hist}, Trend={trend}, SocialBullish={bullish_pct}%
新闻:
{headlines}
请输出 BUY/SELL/HOLD 与不超过3句理由。
"""

        try:
            response = self.call_llm(prompt, "你是多头研究员，强调上涨催化")
            signal = self._extract_signal(response)
            confidence = 0.62
        except Exception:
            signal, confidence, response = self._fallback(rsi14, macd_hist, trend, bullish_pct)

        return AnalysisResult(
            agent_name=self.name,
            signal=signal,
            confidence=confidence,
            reasoning=response,
            indicators={
                "rsi14": rsi14,
                "macd_hist": macd_hist,
                "trend": trend,
                "bullish_pct": bullish_pct,
            },
            risks=["多头论证可能忽略尾部风险"],
        )

    def _extract_signal(self, text: str) -> str:
        upper = text.upper()
        if "BUY" in upper or "买入" in text:
            return "BUY"
        if "SELL" in upper or "卖出" in text:
            return "SELL"
        return "HOLD"

    def _fallback(self, rsi14: float, macd_hist: float, trend: str, bullish_pct: float):
        if trend == "BULLISH" and macd_hist > 0 and bullish_pct >= 55 and rsi14 < 75:
            return "BUY", 0.6, "规则判断: 趋势与动量同向，社媒情绪偏多。"
        return "HOLD", 0.5, "规则判断: 多头证据不足，暂不追高。"
