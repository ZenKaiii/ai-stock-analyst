"""
股票分析主类 - 整合所有Agent
"""
from typing import Dict, List
from datetime import datetime

from agents.base import AnalysisResult
from agents.technical import TechnicalAnalyst
from agents.news import NewsAnalyst
from agents.social import SocialMediaAnalyst
from agents.portfolio import PortfolioManager


class StockAnalyzer:
    """股票分析器 - 协调各Agent进行综合分析"""
    
    def __init__(self):
        self.agents = {
            "technical": TechnicalAnalyst(),
            "news": NewsAnalyst(),
            "social": SocialMediaAnalyst(),
        }
        self.portfolio_manager = PortfolioManager()
    
    def analyze(self, symbol: str, data: Dict) -> Dict:
        """
        执行完整分析流程
        
        Args:
            symbol: 股票代码
            data: 包含价格、新闻、社媒等数据的字典
            
        Returns:
            Dict: 完整分析结果
        """
        analyses = []
        
        # 技术面分析
        if "price_data" in data:
            tech_result = self.agents["technical"].analyze(data)
            analyses.append(tech_result)
        
        # 新闻分析
        if "news" in data and data["news"]:
            news_result = self.agents["news"].analyze(data)
            analyses.append(news_result)
        
        # 社媒分析
        if "social_data" in data:
            social_result = self.agents["social"].analyze(data)
            analyses.append(social_result)
        
        # 投资组合决策
        decision_data = {
            "symbol": symbol,
            "analyses": analyses,
            "price_data": data.get("price_data", {})
        }
        decision = self.portfolio_manager.analyze(decision_data)
        
        return {
            "symbol": symbol,
            "decision": {
                "signal": decision.signal,
                "confidence": round(decision.confidence * 100, 1),
                "rationale": decision.reasoning,
                "entry_price": decision.indicators.get("entry_price"),
                "stop_loss": decision.indicators.get("stop_loss"),
                "target_price": decision.indicators.get("target_price"),
                "position_size": decision.indicators.get("position_size")
            },
            "analyses": [
                {
                    "agent": a.agent_name,
                    "signal": a.signal,
                    "confidence": a.confidence,
                    "reasoning": a.reasoning
                }
                for a in analyses
            ],
            "timestamp": datetime.now().isoformat()
        }


def analyze_stock(symbol: str, price_data: Dict = None, 
                  news: List = None, social_data: Dict = None) -> Dict:
    """
    分析单个股票的便捷函数
    
    Args:
        symbol: 股票代码
        price_data: 价格数据
        news: 新闻列表
        social_data: 社交媒体数据
        
    Returns:
        Dict: 分析结果
    """
    analyzer = StockAnalyzer()
    data = {"symbol": symbol}
    
    if price_data:
        data["price_data"] = price_data
    if news:
        data["news"] = news
    if social_data:
        data["social_data"] = social_data
    
    return analyzer.analyze(symbol, data)
