"""
社媒情绪分析Agent
"""
from typing import Dict
from src.agents.base import BaseAgent, AnalysisResult


class SocialMediaAnalyst(BaseAgent):
    """社交媒体情绪分析Agent"""
    
    def __init__(self):
        super().__init__("SocialMediaAnalyst")
    
    def analyze(self, data: Dict) -> AnalysisResult:
        """
        基于社交媒体讨论进行情绪分析
        
        Args:
            data: 包含社媒数据的字典
            
        Returns:
            AnalysisResult: 分析结果
        """
        symbol = data.get("symbol", "")
        social_data = data.get("social_data", {})
        
        sentiment = social_data.get("sentiment", {})
        posts = social_data.get("posts", [])
        
        bullish_pct = sentiment.get("bullish_pct", 50)
        bearish_pct = sentiment.get("bearish_pct", 50)
        total = social_data.get("total", 0)
        
        # 基于情绪数据判断信号
        if bullish_pct > 60:
            signal = "BUY"
            confidence = (bullish_pct - 50) / 100 + 0.5
        elif bearish_pct > 60:
            signal = "SELL"
            confidence = (bearish_pct - 50) / 100 + 0.5
        else:
            signal = "HOLD"
            confidence = 0.5
        
        reasoning = f"""
社交媒体情绪分析:
- 看涨: {bullish_pct}% ({sentiment.get('bullish', 0)} 帖子)
- 看跌: {bearish_pct}% ({sentiment.get('bearish', 0)} 帖子)
- 总讨论数: {total}

基于社区情绪，给出{signal}信号。
"""
        
        return AnalysisResult(
            agent_name=self.name,
            signal=signal,
            confidence=min(confidence, 0.9),
            reasoning=reasoning,
            indicators=sentiment,
            risks=["社媒情绪可能受操纵", "散户情绪可能快速反转"]
        )
