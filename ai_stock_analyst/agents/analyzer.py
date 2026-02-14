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
        self.agent_pipeline = ["technical", "anomaly", "fundamental", "news", "bull", "bear", "social", "risk"]
        self.portfolio_manager = PortfolioManager()

    def register_agent(self, key: str, agent, append_pipeline: bool = True) -> None:
        """注册新Agent，便于后续扩展/测试注入。"""
        self.agents[key] = agent
        if append_pipeline and key not in self.agent_pipeline:
            self.agent_pipeline.append(key)

    def list_agents(self) -> List[str]:
        return list(self.agent_pipeline)
    
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
        
        risk_result = None
        for key in self.agent_pipeline:
            if key in {"technical", "anomaly", "fundamental"} and "price_data" not in data:
                continue
            if key in {"news", "bull", "bear"} and not data.get("news"):
                continue
            if key == "social" and "social_data" not in data:
                continue

            agent = self.agents.get(key)
            if not agent:
                continue
            result = agent.analyze(data)
            analyses.append(result)
            if key == "risk":
                risk_result = result

        if risk_result is None:
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
