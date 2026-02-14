"""
流动性与成交质量 Agent
"""
from __future__ import annotations

from typing import Dict, List

from ai_stock_analyst.agents.base import AnalysisResult, BaseAgent


class LiquidityQualityAgent(BaseAgent):
    """评估交易可执行性与流动性质量。"""

    def __init__(self):
        super().__init__("LiquidityQualityAgent")

    def analyze(self, data: Dict) -> AnalysisResult:
        price_data = data.get("price_data", {}) or {}
        history = price_data.get("history")

        if history is None or getattr(history, "empty", True) or len(history) < 25:
            return AnalysisResult(
                agent_name=self.name,
                signal="HOLD",
                confidence=0.45,
                reasoning="- 历史成交数据不足，暂不做流动性判断。",
                indicators={},
                risks=["流动性数据不足"],
            )

        close = history["Close"].dropna()
        volume = history["Volume"].dropna()
        open_px = history["Open"].dropna()

        if close.empty or volume.empty:
            return AnalysisResult(
                agent_name=self.name,
                signal="HOLD",
                confidence=0.45,
                reasoning="- 关键成交字段缺失，暂不做流动性判断。",
                indicators={},
                risks=["流动性字段缺失"],
            )

        current_price = float(close.iloc[-1])
        current_volume = float(volume.iloc[-1])
        avg_volume_20 = float(volume.tail(20).mean())
        avg_dollar_volume_20 = float((close.tail(20) * volume.tail(20)).mean())
        turnover_ratio = (current_volume / avg_volume_20) if avg_volume_20 > 0 else 0.0

        gap_pct = 0.0
        if len(close) >= 2 and len(open_px) >= 1 and float(close.iloc[-2]) > 0:
            gap_pct = (float(open_px.iloc[-1]) / float(close.iloc[-2]) - 1) * 100

        volatility_20d = float(price_data.get("volatility_20d", 0) or 0)

        score = 0.0
        reasons: List[str] = []

        if avg_dollar_volume_20 >= 1_000_000_000:
            score += 1.2
            reasons.append(f"20日平均成交额较高(${avg_dollar_volume_20/1e9:.2f}B)")
        elif avg_dollar_volume_20 >= 200_000_000:
            score += 0.6
            reasons.append(f"20日平均成交额中等(${avg_dollar_volume_20/1e6:.0f}M)")
        else:
            score -= 1.0
            reasons.append(f"20日平均成交额偏低(${avg_dollar_volume_20/1e6:.0f}M)")

        if 0.8 <= turnover_ratio <= 2.5:
            score += 0.5
            reasons.append(f"当日成交活跃度正常({turnover_ratio:.2f}x)")
        elif turnover_ratio > 4.0 or turnover_ratio < 0.4:
            score -= 0.5
            reasons.append(f"当日成交活跃度异常({turnover_ratio:.2f}x)")

        if volatility_20d <= 2.5:
            score += 0.4
            reasons.append(f"20日波动率可控({volatility_20d:.2f}%)")
        elif volatility_20d >= 4.0:
            score -= 0.6
            reasons.append(f"20日波动率偏高({volatility_20d:.2f}%)")

        if abs(gap_pct) >= 3.0:
            score -= 0.4
            reasons.append(f"跳空幅度较大({gap_pct:.2f}%)")

        if score >= 1.0:
            signal = "BUY"
        elif score <= -1.0:
            signal = "SELL"
        else:
            signal = "HOLD"

        confidence = min(0.8, 0.45 + abs(score) * 0.12)

        return AnalysisResult(
            agent_name=self.name,
            signal=signal,
            confidence=confidence,
            reasoning="\n".join(f"- {line}" for line in reasons),
            indicators={
                "liquidity_score": round(score, 3),
                "current_price": round(current_price, 2),
                "current_volume": round(current_volume, 0),
                "avg_volume_20": round(avg_volume_20, 0),
                "avg_dollar_volume_20": round(avg_dollar_volume_20, 2),
                "turnover_ratio": round(turnover_ratio, 2),
                "gap_pct": round(gap_pct, 2),
                "volatility_20d": volatility_20d,
            },
            risks=[r for r in reasons if ("偏低" in r or "异常" in r or "偏高" in r)],
        )
