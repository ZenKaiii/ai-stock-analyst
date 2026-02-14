"""
投资组合决策Agent
"""
from typing import Dict, List
from ai_stock_analyst.agents.base import BaseAgent, AnalysisResult


class PortfolioManager(BaseAgent):
    """投资组合经理Agent - 综合各分析师意见做出最终决策"""
    
    def __init__(self):
        super().__init__("PortfolioManager")
    
    def analyze(self, data: Dict) -> AnalysisResult:
        """
        综合各Agent分析结果做出最终决策
        
        Args:
            data: 包含各Agent分析结果和股票数据的字典
            
        Returns:
            AnalysisResult: 最终决策
        """
        symbol = data.get("symbol", "")
        analyses = data.get("analyses", [])
        price_data = data.get("price_data", {})
        risk_assessment = data.get("risk_assessment", {})
        
        if not analyses:
            return AnalysisResult(
                agent_name=self.name,
                signal="HOLD",
                confidence=0.0,
                reasoning="没有分析数据",
                indicators={},
                risks=["缺乏分析数据"]
            )
        
        # 风险管理Agent不参与方向投票，仅作为闸门输入
        directional = [a for a in analyses if a.agent_name != "RiskManager"]
        if not directional:
            directional = analyses

        # 统计各Agent信号
        buy_votes = sum(1 for a in directional if a.signal == "BUY")
        sell_votes = sum(1 for a in directional if a.signal == "SELL")
        hold_votes = len(directional) - buy_votes - sell_votes
        
        # 加权置信度
        avg_confidence = sum(a.confidence for a in directional) / len(directional)
        score_100 = self._build_direction_score(directional)
        
        # 确定最终信号
        if buy_votes > sell_votes and buy_votes > hold_votes:
            signal = "BUY"
        elif sell_votes > buy_votes and sell_votes > hold_votes:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        # 风险闸门：在最终输出前做信号降级
        signal, avg_confidence, risk_note = self._apply_risk_gate(
            signal, avg_confidence, risk_assessment
        )

        # 计算建议价格
        current_price = price_data.get("current_price", 0)
        atr_pct = float(price_data.get("atr_pct", 0) or 0)
        if current_price > 0:
            entry_price = round(current_price, 2)
            # 波动越大，止损与目标越保守
            stop_loss_ratio = 0.95 if atr_pct < 4 else 0.97
            target_ratio = 1.10 if atr_pct < 4 else 1.06
            stop_loss = round(current_price * stop_loss_ratio, 2)
            target_price = round(current_price * target_ratio, 2)
        else:
            entry_price = stop_loss = target_price = 0

        position_size = risk_assessment.get("max_position_size", "5-10%")
        
        reasoning = f"""
综合决策分析:
- 买入投票: {buy_votes}
- 卖出投票: {sell_votes}
- 持有投票: {hold_votes}
- 平均置信度: {avg_confidence:.1%}
- 综合评分: {score_100:.1f}/100
- 风险闸门: {risk_note}

最终信号: {signal}
建议入场价: ${entry_price}
止损价: ${stop_loss}
目标价: ${target_price}
建议仓位: {position_size}
"""
        
        return AnalysisResult(
            agent_name=self.name,
            signal=signal,
            confidence=avg_confidence,
            reasoning=reasoning,
            indicators={
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "target_price": target_price,
                "position_size": position_size,
                "risk_override": bool(risk_assessment.get("triggered", False)),
                "risk_level": risk_assessment.get("risk_level", "LOW"),
                "score_100": round(score_100, 1),
            },
            risks=["多Agent共识可能仍不准确", "建议结合个人判断"]
        )

    def _apply_risk_gate(self, signal: str, confidence: float, risk_assessment: Dict):
        triggered = bool(risk_assessment.get("triggered", False))
        risk_level = risk_assessment.get("risk_level", "LOW")
        triggers = risk_assessment.get("triggers", [])

        if not triggered:
            return signal, confidence, "LOW(未触发)"

        note = f"{risk_level}({';'.join(triggers) if triggers else 'triggered'})"

        # 高风险优先压制做多信号；做空信号通常不做降级。
        if signal == "BUY":
            return "HOLD", max(confidence * 0.75, 0.35), note
        return signal, max(confidence * 0.9, 0.3), note

    def _build_direction_score(self, analyses: List[AnalysisResult]) -> float:
        """将多Agent方向与置信度映射为 0-100 分，便于排序展示。"""
        if not analyses:
            return 50.0

        weights = {
            "MacroRegimeAgent": 1.1,
            "TechnicalAnalyst": 1.0,
            "LiquidityQualityAgent": 1.0,
            "AnomalyAgent": 0.9,
            "FundamentalAnalyst": 1.2,
            "NewsAnalyst": 1.0,
            "BullResearcher": 0.9,
            "BearResearcher": 0.9,
            "SocialMediaAnalyst": 0.8,
        }
        signal_num = {"BUY": 1.0, "HOLD": 0.0, "SELL": -1.0}

        weighted_sum = 0.0
        max_abs = 0.0
        for item in analyses:
            w = float(weights.get(item.agent_name, 1.0))
            conf = max(0.2, min(float(item.confidence), 1.0))
            s = signal_num.get(item.signal, 0.0)
            weighted_sum += w * conf * s
            max_abs += w * conf

        if max_abs <= 0:
            return 50.0
        norm = max(-1.0, min(1.0, weighted_sum / max_abs))
        return 50 + norm * 50
