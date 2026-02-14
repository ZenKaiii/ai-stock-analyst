"""
股票推荐Agent - 从新闻和社交媒体中发现热门股票
"""
import re
from typing import Dict, List

from ai_stock_analyst.agents.base import BaseAgent, AnalysisResult
from ai_stock_analyst.rss import fetch_news
from ai_stock_analyst.data.fetcher import fetch_stock_price


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

# Known major US stock tickers for better matching
KNOWN_TICKERS = {
    # Tech
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", "TSLA", "AMD", "INTC",
    "ORCL", "CRM", "ADBE", "CSCO", "IBM", "QCOM", "TXN", "AVGO", "NOW", "SNOW",
    "PANW", "CRWD", "NET", "DDOG", "ZS", "MDB", "TEAM", "WDAY", "OKTA", "SPLK",
    # Finance
    "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "AXP", "V", "MA", "PYPL", "SQ",
    # Consumer
    "WMT", "TGT", "COST", "HD", "LOW", "NKE", "SBUX", "MCD", "DIS", "CMCSA",
    # Healthcare
    "JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY", "TMO", "ABT", "DHR", "BMY",
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO",
    # Industrial
    "BA", "CAT", "GE", "HON", "UPS", "RTX", "LMT", "DE", "MMM",
    # Other
    "BRK.B", "BRK.A", "SPY", "QQQ", "IWM", "DIA", "VOO", "VTI", "ARKK",
    # Chinese ADRs
    "BABA", "JD", "PDD", "BIDU", "NIO", "XPEV", "LI", "BILI", "TAL", "EDU",
    "NTES", "TME", "IQ", "HUYA", "DOYU", "MOMO", "YY", "BEKE", "TCHP", "IQE"
}


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
        
        # 用技术面与来源多样性校准推荐质量
        stock_signals = self._enrich_with_market_quality(stock_signals)

        # 排序找出最强的看涨信号
        sorted_stocks = sorted(
            stock_signals.items(),
            key=lambda x: x[1].get("composite_score", x[1]["bullish_score"]),
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
                        "composite_score": round(data.get("composite_score", data["bullish_score"]), 2),
                        "signal": data["signal"],
                        "news_count": data["news_count"],
                        "company_name": data.get("company_name", symbol),
                        "sector": data.get("sector", ""),
                        "industry": data.get("industry", ""),
                        "business": data.get("business", ""),
                        "brief_analysis": data.get("brief_analysis", ""),
                        "recommend_reason": data.get("recommend_reason", ""),
                        "evidence_news": data.get("evidence_news", []),
                    }
                    for symbol, data in top_picks
                ]
            },
            risks=self._extract_risks(top_picks)
        )
    
    def _extract_stock_signals(self, news_items: List) -> Dict:
        stock_signals = {}
        
        for news in news_items:
            title = news.get("title", "")
            title_upper = title.upper()
            source = news.get("source", "")
            
            positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw.upper() in title_upper)
            negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw.upper() in title_upper)
            
            if positive_count == 0 and negative_count == 0:
                sentiment = 0.5
            else:
                sentiment = positive_count / (positive_count + negative_count)
            
            found_tickers = set()
            
            for ticker in KNOWN_TICKERS:
                if re.search(r'\b' + re.escape(ticker) + r'\b', title_upper):
                    found_tickers.add(ticker)

            cashtag_matches = re.findall(r'\$([A-Z]{1,5})\b', title_upper)
            for m in cashtag_matches:
                if m in KNOWN_TICKERS:
                    found_tickers.add(m)
            
            for ticker in found_tickers:
                if ticker not in stock_signals:
                    stock_signals[ticker] = {
                        "signal": "HOLD",
                        "bullish_score": 0.0,
                        "sentiment_score": [],
                        "news_count": 0,
                        "sources": [],
                        "titles": [],
                        "news_items": [],
                        "brief_analysis": "",
                        "evidence_news": [],
                        "recommend_reason": "",
                        "company_name": "",
                        "sector": "",
                        "industry": "",
                        "business": "",
                    }
                
                stock_signals[ticker]["sentiment_score"].append(sentiment)
                stock_signals[ticker]["news_count"] += 1
                stock_signals[ticker]["sources"].append(source)
                stock_signals[ticker]["titles"].append(f"[{source}] {title[:120]}")
                stock_signals[ticker]["news_items"].append(
                    {
                        "title": title[:180],
                        "source": source,
                        "summary": news.get("summary", "")[:260],
                        "link": news.get("link", ""),
                    }
                )
        
        for ticker, data in stock_signals.items():
            if data["sentiment_score"]:
                avg_sentiment = sum(data["sentiment_score"]) / len(data["sentiment_score"])
            else:
                avg_sentiment = 0.5
            
            data["bullish_score"] = avg_sentiment * (1 + min(data["news_count"], 5) * 0.1)
            
            if avg_sentiment > 0.6:
                data["signal"] = "BUY"
            elif avg_sentiment < 0.4:
                data["signal"] = "SELL"
            else:
                data["signal"] = "HOLD"
        
        return stock_signals
    
    def _build_recommendation_text(self, top_picks: List) -> str:
        lines = ["以下为候选股票的简要分析、新闻依据和推荐原因：", ""]
        
        for idx, (symbol, data) in enumerate(top_picks, start=1):
            emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(data["signal"], "⚪")
            evidence_lines = data.get("evidence_news", [])[:2]
            evidence_md = "\n".join(f"- {item}" for item in evidence_lines) if evidence_lines else "- 无"
            company = data.get("company_name") or symbol
            sector = self._to_cn_label(data.get("sector") or "未知板块")
            industry = self._to_cn_label(data.get("industry") or "未知行业")
            business = self._describe_business_for_beginner(company, data.get("business", ""), sector, industry)
            lines.append(
                f"### {idx}. {emoji} {symbol} ({company})\n"
                f"- **结论**: `{data['signal']}`\n"
                f"- **公司/行业**: {sector} / {industry}\n"
                f"- **公司做什么**: {business}\n"
                f"- **简要分析**: {data.get('brief_analysis', '暂无')}\n"
                f"- **推荐原因**: {data.get('recommend_reason', '暂无')}\n"
                f"- **看涨评分**: `{data['bullish_score']:.2f}` | **综合评分**: `{data.get('composite_score', data['bullish_score']):.2f}`\n"
                f"- **新闻依据**:\n{evidence_md}\n\n"
            )
        
        return "\n".join(lines)

    def _enrich_with_market_quality(self, stock_signals: Dict) -> Dict:
        """结合趋势/波动与来源多样性，降低纯新闻噪音。"""
        candidates = sorted(
            stock_signals.items(), key=lambda x: x[1]["news_count"], reverse=True
        )[:12]

        for symbol, data in candidates:
            price = fetch_stock_price(symbol)
            if "error" in price:
                data["composite_score"] = max(data["bullish_score"] * 0.6, 0.0)
                data["brief_analysis"] = "行情数据获取失败，暂按新闻情绪评估。"
                data["evidence_news"] = self._summarize_news_evidence(data.get("news_items", [])[:2])
                data["recommend_reason"] = "仅有新闻侧证据，建议谨慎。"
                continue

            trend = price.get("trend", "NEUTRAL")
            rsi14 = float(price.get("rsi14", 50) or 50)
            macd_hist = float(price.get("macd_hist", 0) or 0)
            atr_pct = float(price.get("atr_pct", 0) or 0)
            data["company_name"] = price.get("name", symbol)
            data["sector"] = price.get("sector", "")
            data["industry"] = price.get("industry", "")
            data["business"] = price.get("business_summary", "")

            momentum = 0.5
            if trend == "BULLISH":
                momentum += 0.2
            if macd_hist > 0:
                momentum += 0.15
            if 45 <= rsi14 <= 70:
                momentum += 0.1
            if atr_pct > 4:
                momentum -= 0.15

            source_diversity = min(len(set(data["sources"])) / 4, 1.0)
            risk_penalty = 0.15 if atr_pct > 4 else 0.0
            composite = (
                data["bullish_score"] * 0.55
                + momentum * 0.30
                + source_diversity * 0.15
                - risk_penalty
            )
            data["composite_score"] = max(composite, 0.0)
            data["evidence_news"] = self._summarize_news_evidence(data.get("news_items", [])[:3])
            data["brief_analysis"] = (
                f"趋势 {trend}，RSI14={rsi14:.1f}，MACD柱={macd_hist:.3f}，ATR%={atr_pct:.2f}。"
            )
            if composite >= 0.75:
                reason = "新闻热度、技术动量与风险控制三方面同向，短期有较强跟踪价值。"
            elif composite >= 0.62:
                reason = "信号中性偏多，但确定性一般，建议小仓位、分批观察。"
            else:
                reason = "证据不足或波动偏高，暂以观察为主，等待更清晰催化。"
            data["recommend_reason"] = reason

        # 未进入候选池的股票退化为原分数
        for _, data in stock_signals.items():
            if "composite_score" not in data:
                data["composite_score"] = data["bullish_score"]
            if not data.get("evidence_news"):
                data["evidence_news"] = self._summarize_news_evidence(data.get("news_items", [])[:2])
            if not data.get("brief_analysis"):
                data["brief_analysis"] = "样本较少，暂缺充分技术确认。"
            if not data.get("recommend_reason"):
                data["recommend_reason"] = "新闻证据不足，建议继续观察。"

        return stock_signals

    def _summarize_news_evidence(self, news_items: List[Dict]) -> List[str]:
        summaries: List[str] = []
        for item in news_items:
            title = item.get("title", "")
            source = item.get("source", "Unknown")
            summary = item.get("summary", "")
            event_cn = self._summarize_news_event(title, summary)
            impact = self._infer_news_impact(title, summary)
            summaries.append(f"[{source}] 事件：{event_cn}；解读：{impact}")
        return summaries

    def _infer_news_impact(self, title: str, summary: str) -> str:
        text = f"{title} {summary}".lower()
        if any(k in text for k in ["beat", "upgrade", "record", "growth", "partnership", "订单", "超预期", "上调"]):
            return "偏利好，通常对应盈利预期或订单增长。"
        if any(k in text for k in ["downgrade", "miss", "lawsuit", "tariff", "sanction", "诉讼", "下调", "关税"]):
            return "偏利空，可能压制利润率或估值。"
        if any(k in text for k in ["earnings", "guidance", "财报", "指引"]):
            return "中性偏事件驱动，需结合财报细节确认方向。"
        return "信息偏中性，建议结合后续价格与成交量确认。"

    def _summarize_news_event(self, title: str, summary: str) -> str:
        text = f"{title} {summary}".strip()
        lower = text.lower()
        if any(k in lower for k in ["earnings", "财报", "guidance", "指引"]):
            return "公司披露业绩或业绩指引更新"
        if any(k in lower for k in ["trump", "tariff", "关税", "sanction", "制裁"]):
            return "政策/地缘政治消息影响相关行业预期"
        if any(k in lower for k in ["partnership", "contract", "订单", "合作", "签约"]):
            return "公司获得合作或订单催化"
        if any(k in lower for k in ["rate", "inflation", "cpi", "利率", "通胀"]):
            return "宏观利率或通胀变化影响估值预期"
        short_title = title.strip()[:50]
        return short_title if short_title else "一般经营动态更新"

    def _to_cn_label(self, text: str) -> str:
        if not text:
            return "未知"
        table = {
            "technology": "科技",
            "consumer cyclical": "可选消费",
            "consumer defensive": "必选消费",
            "financial services": "金融服务",
            "healthcare": "医疗健康",
            "industrials": "工业",
            "energy": "能源",
            "communication services": "通信服务",
            "real estate": "房地产",
            "utilities": "公用事业",
            "basic materials": "原材料",
            "semiconductor": "半导体",
            "software": "软件",
            "internet": "互联网",
            "banks": "银行",
            "oil & gas": "油气",
            "biotechnology": "生物科技",
        }
        lower = text.lower()
        for key, cn in table.items():
            if key in lower:
                return cn
        return text

    def _describe_business_for_beginner(self, company: str, business: str, sector: str, industry: str) -> str:
        source = (business or "").strip()
        if not source:
            return f"{company} 属于 {sector}/{industry} 板块，建议重点关注其营收增长与利润率变化。"
        if re.search(r"[\u4e00-\u9fff]", source):
            return source[:140]

        lower = source.lower()
        if any(k in lower for k in ["chip", "semiconductor", "gpu"]):
            return f"{company} 主要做芯片/算力相关业务，属于科技与半导体方向。"
        if any(k in lower for k in ["software", "cloud", "saas"]):
            return f"{company} 主要做软件或云服务，核心看订阅增长和企业IT支出。"
        if any(k in lower for k in ["bank", "lending", "insurance"]):
            return f"{company} 属于金融业务，盈利通常受利率周期与资产质量影响。"
        if any(k in lower for k in ["retail", "consumer", "store", "e-commerce"]):
            return f"{company} 属于消费零售，主要看消费需求、同店销售和库存周转。"
        if any(k in lower for k in ["drug", "biotech", "pharmaceutical", "medical"]):
            return f"{company} 属于医药医疗方向，关键看产品管线、审批和商业化进度。"
        if any(k in lower for k in ["oil", "gas", "energy"]):
            return f"{company} 属于能源行业，收益通常受油气价格与供需变化影响。"

        return f"{company} 属于 {sector}/{industry} 板块，核心业务可概括为：{source[:120]}。"
    
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
    news_data = {
        "all_news": [
            {"title": n.title, "source": n.source, "summary": n.summary, "link": n.link}
            for n in all_news
        ]
    }
    result = agent.analyze(news_data)
    
    recommendations = []
    if result.indicators.get("top_picks"):
        for pick in result.indicators["top_picks"]:
            recommendations.append({
                "symbol": pick["symbol"],
                "signal": pick["signal"],
                "bullish_score": pick["score"],
                "composite_score": pick.get("composite_score", pick["score"]),
                "news_count": pick["news_count"],
                "brief_analysis": pick.get("brief_analysis", ""),
                "recommend_reason": pick.get("recommend_reason", ""),
                "evidence_news": pick.get("evidence_news", []),
                "company_name": pick.get("company_name", pick["symbol"]),
                "sector": pick.get("sector", ""),
                "industry": pick.get("industry", ""),
                "business": pick.get("business", ""),
            })
    
    return {
        "recommendations": recommendations,
        "summary": result.reasoning,
        "signal": result.signal,
        "confidence": result.confidence
    }
