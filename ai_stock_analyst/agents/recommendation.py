"""
股票推荐Agent - 从新闻和社交媒体中发现热门股票
"""
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ai_stock_analyst.agents.base import BaseAgent, AnalysisResult
from ai_stock_analyst.rss import fetch_news


POSITIVE_KEYWORDS = [
    "upgrade", "beat", "bullish", "upgrade", "outperform", "buy", "recommend",
    "growth", "surge", "rally", "soar", "jump", "gain", "profit", "record",
    "breakthrough", "innovation", "expansion", "partnership", "contract",
    "上调", "增持", "买入", "超预期", "突破", "增长", "利好", "签约"
]

NEGATIVE_KEYWORDS = [
    "downgrade", "miss", "bearish", "underperform", "sell", "cut", "reduce",
    "decline", "crash", "plunge", "drop", "loss", "lawsuit", "investigation",
    "下调", "减持", "卖出", "不及预期", "利空", "亏损", "诉讼", "调查"
]


class RecommendationAgent(BaseAgent):
    """股票推荐Agent - 从新闻/社媒中发现潜在机会"""
    
    def __init__(self):
        super().__init__("RecommendationAgent")
    
    def analyze(self, data: Dict) -> AnalysisResult:
        """
        分析新闻和社交媒体，发现潜在热门股票
        
        Args:
            data: 包含新闻和社媒数据的字典
            
        Returns:
            AnalysisResult: 推荐结果
        """
        all_news = data.get("all_news", [])
        
        if not all_news:
            return AnalysisResult(
                agent_name=self.name,
                signal="HOLD",
                confidence=0.0,
                reasoning="没有找到相关新闻",
                indicators={},
                risks=["缺乏数据"]
            )
        
        # 从新闻中提取股票代码和情绪
        stock_signals = self._extract_stock_signals(all_news)
        
        # 排序找出最强的看涨信号
        sorted_stocks = sorted(
            stock_signals.items(),
            key=lambda x: x[1]["bullish_score"],
            reverse=True
        )
        
        # 取Top 5推荐
        top_picks = sorted_stocks[:5]
        
        if not top_picks:
            return AnalysisResult(
                agent_name=self.name,
                signal="HOLD",
                confidence=0.3,
                reasoning="未发现明显的机会",
                indicators={"stocks_found": 0},
                risks=["市场可能处于观望状态"]
            )
        
        # 构建推荐理由
        recommendation_text = self._build_recommendation_text(top_picks)
        
        bullish_count = sum(1 for _, s in top_picks if s["signal"] == "BUY")
        
        return AnalysisResult(
            agent_name=self.name,
            signal="BUY" if bullish_count >= 3 else "HOLD",
            confidence=min(0.7, bullish_count / 5),
            reasoning=recommendation_text,
            indicators={
                "top_picks": [
                    {
                        "symbol": symbol,
                        "score": round(data["bullish_score"], 2),
                        "signal": data["signal"],
                        "news_count": data["news_count"]
                    }
                    for symbol, data in top_picks
                ]
            },
            risks=self._extract_risks(top_picks)
        )
    
    def _extract_stock_signals(self, news_items: List) -> Dict:
        """从新闻中提取股票信号"""
        stock_signals = {}
        
        # 美股常见股票代码模式
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        
        for news in news_items:
            title = news.get("title", "").upper()
            source = news.get("source", "")
            
            # 简单的情绪分析
            positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw.upper() in title)
            negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw.upper() in title)
            
            if positive_count == 0 and negative_count == 0:
                sentiment = 0.5
            else:
                sentiment = positive_count / (positive_count + negative_count)
            
            # 跳过明显的非股票词汇
            skip_words = {"CEO", "CFO", "CTO", "IPO", "ETF", "API", "USA", "AI", "UK", "EU", "UN", "FDA", "SEC"}
            
            # 尝试从标题中提取股票代码
            potential_tickers = re.findall(ticker_pattern, title)
            
            for ticker in potential_tickers:
                if ticker in skip_words or len(ticker) < 2:
                    continue
                
                if ticker not in stock_signals:
                    stock_signals[ticker] = {
                        "signal": "HOLD",
                        "bullish_score": 0.0,
                        "sentiment_score": [],
                        "news_count": 0,
                        "sources": [],
                        "titles": []
                    }
                
                stock_signals[ticker]["sentiment_score"].append(sentiment)
                stock_signals[ticker]["news_count"] += 1
                stock_signals[ticker]["sources"].append(source)
                stock_signals[ticker]["titles"].append(title[:100])
        
        # 计算综合分数
        for ticker, data in stock_signals.items():
            if data["sentiment_score"]:
                avg_sentiment = sum(data["sentiment_score"]) / len(data["sentiment_score"])
            else:
                avg_sentiment = 0.5
            
            # 综合分数 = 情绪分数 * 新闻数量权重
            data["bullish_score"] = avg_sentiment * (1 + min(data["news_count"], 5) * 0.1)
            
            if avg_sentiment > 0.6:
                data["signal"] = "BUY"
            elif avg_sentiment < 0.4:
                data["signal"] = "SELL"
            else:
                data["signal"] = "HOLD"
        
        return stock_signals
    
    def _build_recommendation_text(self, top_picks: List) -> str:
        """构建推荐文本"""
        lines = ["📈 热门股票发现:\n"]
        
        for symbol, data in top_picks:
            emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(data["signal"], "⚪")
            lines.append(
                f"{emoji} {symbol}: {data['signal']} (评分:{data['bullish_score']:.1f}, "
                f"新闻数:{data['news_count']})"
            )
        
        return "\n".join(lines)
    
    def _extract_risks(self, top_picks: List) -> List[str]:
        """提取风险因素"""
        risks = []
        
        if len(top_picks) < 3:
            risks.append("推荐股票数量较少，建议进一步研究")
        
        for symbol, data in top_picks:
            if data["news_count"] == 1:
                risks.append(f"{symbol} 仅有1条新闻支撑")
        
        return risks if risks else ["市场有风险，投资需谨慎"]


def scan_for_opportunities(max_news: int = 100) -> Dict:
    """
    扫描新闻发现潜在机会股
    
    Args:
        max_news: 最大新闻数量
        
    Returns:
        Dict: 包含热门股票推荐
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("开始扫描热门股票...")
    
    # 获取所有新闻
    all_news = fetch_news(None)[:max_news]
    
    if not all_news:
        logger.warning("没有获取到新闻")
        return {"recommendations": [], "error": "No news available"}
    
    logger.info(f"获取到 {len(all_news)} 条新闻")
    
    # 提取股票信号
    agent = RecommendationAgent()
    news_data = {"all_news": [{"title": n.title, "source": n.source} for n in all_news]}
    result = agent.analyze(news_data)
    
    recommendations = []
    if result.indicators.get("top_picks"):
        for pick in result.indicators["top_picks"]:
            recommendations.append({
                "symbol": pick["symbol"],
                "signal": pick["signal"],
                "bullish_score": pick["score"],
                "news_count": pick["news_count"]
            })
    
    return {
        "recommendations": recommendations,
        "summary": result.reasoning,
        "signal": result.signal,
        "confidence": result.confidence
    }
