"""
空头研究员 Agent
"""
from typing import Dict

from ai_stock_analyst.agents.base import AnalysisResult, BaseAgent


class BearResearcher(BaseAgent):
    def __init__(self):
        super().__init__("BearResearcher")

    def analyze(self, data: Dict) -> AnalysisResult:
        symbol = data.get("symbol", "")
        price_data = data.get("price_data", {})
        news_items = data.get("news", [])
        social = data.get("social_data", {}).get("sentiment", {})

        rsi14 = float(price_data.get("rsi14", 50) or 50)
        atr_pct = float(price_data.get("atr_pct", 0) or 0)
        change_percent = float(price_data.get("change_percent", 0) or 0)
        bearish_pct = float(social.get("bearish_pct", 50) or 50)

        headlines = "\n".join(f"- {n.get('title', '')}" for n in news_items[:6])
        prompt = f"""
作为空头研究员，请为 {symbol} 提供最强空头论据：
RSI14={rsi14}, ATR%={atr_pct}, Change%={change_percent}, SocialBearish={bearish_pct}%
新闻:
{headlines}
请输出 BUY/SELL/HOLD 与不超过3句理由。
"""

        try:
            response = self.call_llm(prompt, "你是空头研究员，强调下跌与回撤风险")
            signal = self._extract_signal(response)
            confidence = 0.62
        except Exception:
            signal, confidence, response = self._fallback(rsi14, atr_pct, change_percent, bearish_pct)

        return AnalysisResult(
            agent_name=self.name,
            signal=signal,
            confidence=confidence,
            reasoning=response,
            indicators={
                "rsi14": rsi14,
                "atr_pct": atr_pct,
                "change_percent": change_percent,
                "bearish_pct": bearish_pct,
            },
            risks=["空头论证可能错过反弹"],
        )

    def _extract_signal(self, text: str) -> str:
        upper = text.upper()
        if "SELL" in upper or "卖出" in text:
            return "SELL"
        if "BUY" in upper or "买入" in text:
            return "BUY"
        return "HOLD"

    def _fallback(self, rsi14: float, atr_pct: float, change_percent: float, bearish_pct: float):
        if (rsi14 > 78 and change_percent > 4) or (atr_pct > 4 and bearish_pct >= 55):
            return "SELL", 0.62, "规则判断: 波动与情绪指向回撤风险。"
        return "HOLD", 0.5, "规则判断: 空头证据不足，维持观望。"
