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
        revenue_growth = float(price_data.get("revenue_growth", 0) or 0)
        earnings_growth = float(price_data.get("earnings_growth", 0) or 0)
        profit_margins = float(price_data.get("profit_margins", 0) or 0)
        operating_margins = float(price_data.get("operating_margins", 0) or 0)
        return_on_equity = float(price_data.get("return_on_equity", 0) or 0)
        debt_to_equity = float(price_data.get("debt_to_equity", 0) or 0)
        current_ratio = float(price_data.get("current_ratio", 0) or 0)
        quick_ratio = float(price_data.get("quick_ratio", 0) or 0)

        news_headlines = "\n".join(
            f"- {item.get('title', '')}" for item in news_items[:5]
        )

        quality_score, quality_reasons = self._fundamental_quality_score(
            pe_ratio=pe_ratio,
            revenue_growth=revenue_growth,
            earnings_growth=earnings_growth,
            profit_margins=profit_margins,
            operating_margins=operating_margins,
            return_on_equity=return_on_equity,
            debt_to_equity=debt_to_equity,
            current_ratio=current_ratio,
            quick_ratio=quick_ratio,
        )

        prompt = f"""
请从基本面角度评估 {symbol}：
PE: {pe_ratio}
市值: {market_cap}
营收增速: {revenue_growth}
利润增速: {earnings_growth}
净利率: {profit_margins}
ROE: {return_on_equity}
负债权益比: {debt_to_equity}
流动比率: {current_ratio}
速动比率: {quick_ratio}
趋势: {trend}
当日涨跌: {change_percent}%
财报稳定性评分(规则基线): {quality_score}/100
相关新闻:
{news_headlines}

输出:
1) BUY/SELL/HOLD
2) 不超过3句理由
"""

        try:
            response = self.call_llm(prompt, "你是审慎的基本面分析师")
            signal = self._extract_signal(response)
            confidence = max(0.55, min(0.8, quality_score / 100))
            response = (
                f"{response}\n\n规则化财报稳定性评分: {quality_score}/100\n"
                + "\n".join(f"- {r}" for r in quality_reasons[:4])
            )
        except Exception:
            signal, confidence, response = self._fallback(
                pe_ratio, trend, change_percent, quality_score, quality_reasons
            )

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
                "fundamental_score_100": quality_score,
                "revenue_growth": revenue_growth,
                "earnings_growth": earnings_growth,
                "profit_margins": profit_margins,
                "operating_margins": operating_margins,
                "return_on_equity": return_on_equity,
                "debt_to_equity": debt_to_equity,
                "current_ratio": current_ratio,
                "quick_ratio": quick_ratio,
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

    def _fallback(
        self,
        pe_ratio: float,
        trend: str,
        change_percent: float,
        quality_score: float,
        quality_reasons,
    ):
        if quality_score >= 65 and trend == "BULLISH" and change_percent > -3:
            return (
                "BUY",
                0.66,
                "规则判断: 财报稳定性较好且趋势偏多。\n" + "\n".join(f"- {r}" for r in quality_reasons[:4]),
            )
        if quality_score <= 40 or (pe_ratio and pe_ratio > 80 and change_percent < -2):
            return (
                "SELL",
                0.65,
                "规则判断: 财报稳定性偏弱或估值过高。\n" + "\n".join(f"- {r}" for r in quality_reasons[:4]),
            )
        return (
            "HOLD",
            0.55,
            "规则判断: 财报与估值信号分化，维持观望。\n" + "\n".join(f"- {r}" for r in quality_reasons[:4]),
        )

    def _fundamental_quality_score(
        self,
        pe_ratio: float,
        revenue_growth: float,
        earnings_growth: float,
        profit_margins: float,
        operating_margins: float,
        return_on_equity: float,
        debt_to_equity: float,
        current_ratio: float,
        quick_ratio: float,
    ):
        score = 50.0
        reasons = []

        if revenue_growth > 0.08:
            score += 10
            reasons.append("营收增速较好")
        elif revenue_growth < 0:
            score -= 8
            reasons.append("营收增速为负")

        if earnings_growth > 0.08:
            score += 10
            reasons.append("利润增速较好")
        elif earnings_growth < 0:
            score -= 8
            reasons.append("利润增速为负")

        if profit_margins > 0.15:
            score += 8
            reasons.append("净利率较高")
        elif profit_margins < 0.05:
            score -= 6
            reasons.append("净利率偏低")

        if operating_margins > 0.15:
            score += 5
            reasons.append("经营利润率健康")

        if return_on_equity > 0.12:
            score += 8
            reasons.append("ROE表现较好")
        elif return_on_equity < 0.06:
            score -= 6
            reasons.append("ROE偏弱")

        if debt_to_equity > 200:
            score -= 8
            reasons.append("杠杆较高(负债权益比偏高)")
        elif debt_to_equity and debt_to_equity < 80:
            score += 4
            reasons.append("资产负债结构较稳")

        if current_ratio >= 1.2:
            score += 4
            reasons.append("流动比率较稳")
        if quick_ratio >= 1.0:
            score += 3
            reasons.append("速动比率较稳")

        if pe_ratio:
            if pe_ratio > 80:
                score -= 6
                reasons.append("估值偏高")
            elif pe_ratio < 35:
                score += 4
                reasons.append("估值相对可接受")

        score = max(0.0, min(100.0, score))
        if not reasons:
            reasons.append("财报关键字段不足，评分可信度有限")
        return round(score, 1), reasons
