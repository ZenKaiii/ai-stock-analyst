"""
股票分析主类 - 整合所有Agent
"""
from typing import Dict, List, Optional
from datetime import datetime

from ai_stock_analyst.agents.base import AnalysisResult
from ai_stock_analyst.agents.technical import TechnicalAnalyst
from ai_stock_analyst.agents.news import NewsAnalyst
from ai_stock_analyst.agents.social import SocialMediaAnalyst
from ai_stock_analyst.agents.portfolio import PortfolioManager
from ai_stock_analyst.agents.anomaly import AnomalyAgent
from ai_stock_analyst.agents.fundamental import FundamentalAnalyst
from ai_stock_analyst.agents.bull_researcher import BullResearcher
from ai_stock_analyst.agents.bear_researcher import BearResearcher
from ai_stock_analyst.agents.risk_manager import RiskManager


class StockAnalyzer:
    """股票分析器 - 协调各Agent进行综合分析"""
    
    def __init__(self):
        self.agents = {
            "technical": TechnicalAnalyst(),
            "news": NewsAnalyst(),
            "social": SocialMediaAnalyst(),
            "anomaly": AnomalyAgent(),
            "fundamental": FundamentalAnalyst(),
            "bull": BullResearcher(),
            "bear": BearResearcher(),
            "risk": RiskManager(),
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
            
            anomaly_result = self.agents["anomaly"].analyze(data)
            analyses.append(anomaly_result)
        
        # 基本面分析
        if "price_data" in data:
            fundamental_result = self.agents["fundamental"].analyze(data)
            analyses.append(fundamental_result)

        # 新闻分析
        if "news" in data and data["news"]:
            news_result = self.agents["news"].analyze(data)
            analyses.append(news_result)

            bull_result = self.agents["bull"].analyze(data)
            bear_result = self.agents["bear"].analyze(data)
            analyses.extend([bull_result, bear_result])
        
        # 社媒分析
        if "social_data" in data:
            social_result = self.agents["social"].analyze(data)
            analyses.append(social_result)

        # 风险闸门分析（在最终决策前）
        risk_result = self.agents["risk"].analyze(data)
        analyses.append(risk_result)
        
        # 投资组合决策
        decision_data = {
            "symbol": symbol,
            "analyses": analyses,
            "price_data": data.get("price_data", {}),
            "risk_assessment": risk_result.indicators,
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
            "news": data.get("news", [])[:5],
            "timestamp": datetime.now().isoformat()
        }


def analyze_stock(symbol: str, data: Optional[Dict] = None) -> Dict:
    """
    分析单个股票的便捷函数

    Args:
        symbol: 股票代码
        data: 包含价格、新闻、社媒等数据的字典

    Returns:
        Dict: 分析结果
    """
    analyzer = StockAnalyzer()
    if data is None:
        data = {"symbol": symbol}
    else:
        data["symbol"] = symbol

    return analyzer.analyze(symbol, data)
