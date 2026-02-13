"""
技术面分析Agent
"""
from typing import Dict
from agents.base import BaseAgent, AnalysisResult


class TechnicalAnalyst(BaseAgent):
    """技术面分析Agent"""
    
    def __init__(self):
        super().__init__("TechnicalAnalyst")
    
    def analyze(self, data: Dict) -> AnalysisResult:
        """
        基于技术指标进行分析
        
        Args:
            data: 包含股票数据的字典
            
        Returns:
            AnalysisResult: 分析结果
        """
        symbol = data.get("symbol", "")
        price_data = data.get("price_data", {})
        
        # 提取关键指标
        current_price = price_data.get("current_price", 0)
        ma5 = price_data.get("ma5", 0)
        ma20 = price_data.get("ma20", 0)
        trend = price_data.get("trend", "NEUTRAL")
        change_percent = price_data.get("change_percent", 0)
        
        # 构建分析prompt
        prompt = f"""
分析 {symbol} 的技术面情况：

当前价格: ${current_price}
5日均线: ${ma5}
20日均线: ${ma20}
趋势: {trend}
涨跌: {change_percent}%

请给出：
1. 交易信号 (BUY/SELL/HOLD)
2. 简要理由（2-3句话）
"""
        
        # 调用LLM分析
        try:
            response = self.call_llm(prompt, "你是专业技术分析师，擅长技术分析")
            signal = self._extract_signal(response)
            confidence = 0.7 if trend != "NEUTRAL" else 0.5
        except Exception as e:
            # LLM失败时使用规则判断
            signal = self._rule_based_signal(trend, change_percent)
            response = f"基于规则判断: {signal}"
            confidence = 0.5
        
        return AnalysisResult(
            agent_name=self.name,
            signal=signal,
            confidence=confidence,
            reasoning=response,
            indicators={
                "price": current_price,
                "ma5": ma5,
                "ma20": ma20,
                "trend": trend,
                "change_percent": change_percent
            },
            risks=["技术分析有滞后性", "单一指标可能失效"]
        )
    
    def _extract_signal(self, text: str) -> str:
        """从LLM响应中提取信号"""
        text_upper = text.upper()
        if "BUY" in text_upper or "买入" in text:
            return "BUY"
        elif "SELL" in text_upper or "卖出" in text:
            return "SELL"
        return "HOLD"
    
    def _rule_based_signal(self, trend: str, change_percent: float) -> str:
        """基于规则的判断（LLM失败时使用）"""
        if trend == "BULLISH" and change_percent > 2:
            return "BUY"
        elif trend == "BEARISH" and change_percent < -2:
            return "SELL"
        return "HOLD"
