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
        
        if not analyses:
            return AnalysisResult(
                agent_name=self.name,
                signal="HOLD",
                confidence=0.0,
                reasoning="没有分析数据",
                indicators={},
                risks=["缺乏分析数据"]
            )
        
        # 统计各Agent信号
        buy_votes = sum(1 for a in analyses if a.signal == "BUY")
        sell_votes = sum(1 for a in analyses if a.signal == "SELL")
        hold_votes = len(analyses) - buy_votes - sell_votes
        
        # 加权置信度
        avg_confidence = sum(a.confidence for a in analyses) / len(analyses)
        
        # 确定最终信号
        if buy_votes > sell_votes and buy_votes > hold_votes:
            signal = "BUY"
        elif sell_votes > buy_votes and sell_votes > hold_votes:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        # 计算建议价格
        current_price = price_data.get("current_price", 0)
        if current_price > 0:
            entry_price = round(current_price, 2)
            stop_loss = round(current_price * 0.95, 2)
            target_price = round(current_price * 1.1, 2)
        else:
            entry_price = stop_loss = target_price = 0
        
        reasoning = f"""
综合决策分析:
- 买入投票: {buy_votes}
- 卖出投票: {sell_votes}
- 持有投票: {hold_votes}
- 平均置信度: {avg_confidence:.1%}

最终信号: {signal}
建议入场价: ${entry_price}
止损价: ${stop_loss}
目标价: ${target_price}
建议仓位: 5-10%
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
                "position_size": "5-10%"
            },
            risks=["多Agent共识可能仍不准确", "建议结合个人判断"]
        )
