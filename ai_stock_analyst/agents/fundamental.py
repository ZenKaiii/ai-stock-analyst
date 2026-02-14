"""
基本面分析 Agent
"""
from typing import Dict

from ai_stock_analyst.agents.base import AnalysisResult, BaseAgent


class FundamentalAnalyst(BaseAgent):
    def __init__(self):
        super().__init__("FundamentalAnalyst")

    def analyze(self, data: Dict) -> AnalysisResult:
        symbol = data.get("symbol", "")
        price_data = data.get("price_data", {})
        news_items = data.get("news", [])

        pe_ratio = float(price_data.get("pe_ratio", 0) or 0)
        market_cap = float(price_data.get("market_cap", 0) or 0)
        trend = price_data.get("trend", "NEUTRAL")
        change_percent = float(price_data.get("change_percent", 0) or 0)

        news_headlines = "\n".join(
            f"- {item.get('title', '')}" for item in news_items[:5]
        )

        prompt = f"""
请从基本面角度评估 {symbol}：
PE: {pe_ratio}
市值: {market_cap}
趋势: {trend}
当日涨跌: {change_percent}%
相关新闻:
{news_headlines}

输出:
1) BUY/SELL/HOLD
2) 不超过3句理由
"""

        try:
            response = self.call_llm(prompt, "你是审慎的基本面分析师")
            signal = self._extract_signal(response)
            confidence = 0.65
        except Exception:
            signal, confidence, response = self._fallback(pe_ratio, trend, change_percent)

        return AnalysisResult(
            agent_name=self.name,
            signal=signal,
            confidence=confidence,
            reasoning=response,
            indicators={
                "pe_ratio": pe_ratio,
                "market_cap": market_cap,
                "trend": trend,
                "change_percent": change_percent,
            },
            risks=["财务信息与估值存在滞后", "基本面与短期价格可能背离"],
        )

    def _extract_signal(self, text: str) -> str:
        upper = text.upper()
        if "BUY" in upper or "买入" in text:
            return "BUY"
        if "SELL" in upper or "卖出" in text:
            return "SELL"
        return "HOLD"

    def _fallback(self, pe_ratio: float, trend: str, change_percent: float):
        if pe_ratio and pe_ratio < 35 and trend == "BULLISH" and change_percent > -3:
            return "BUY", 0.6, "规则判断: 估值相对可接受且趋势偏多。"
        if pe_ratio and pe_ratio > 80 and change_percent < -2:
            return "SELL", 0.6, "规则判断: 估值过高且价格转弱。"
        return "HOLD", 0.5, "规则判断: 基本面信号不充分，维持观望。"
