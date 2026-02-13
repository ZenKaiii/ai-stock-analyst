"""
新闻分析Agent
"""
from typing import Dict, List
from ai_stock_analyst.agents.base import BaseAgent, AnalysisResult


class NewsAnalyst(BaseAgent):
    """新闻舆情分析Agent"""
    
    def __init__(self):
        super().__init__("NewsAnalyst")
    
    def analyze(self, data: Dict) -> AnalysisResult:
        """
        基于新闻进行情绪分析
        
        Args:
            data: 包含新闻数据的字典
            
        Returns:
            AnalysisResult: 分析结果
        """
        symbol = data.get("symbol", "")
        news_items = data.get("news", [])
        
        if not news_items:
            return AnalysisResult(
                agent_name=self.name,
                signal="HOLD",
                confidence=0.5,
                reasoning="没有相关新闻",
                indicators={"news_count": 0},
                risks=["缺乏新闻数据"]
            )
        
        # 格式化新闻
        news_text = "\n".join([
            f"- [{n.get('source', 'Unknown')}] {n.get('title', '')}"
            for n in news_items[:10]
        ])
        
        prompt = f"""
基于以下关于 {symbol} 的最新新闻，分析市场情绪：

{news_text}

请分析：
1. 整体情绪（正面/负面/中性）
2. 重要事件或催化剂
3. 交易信号建议（BUY/SELL/HOLD）
"""
        
        try:
            response = self.call_llm(prompt, "你是财经新闻分析师")
            sentiment_score = self._analyze_sentiment(response)
            signal = self._extract_signal(response)
            confidence = abs(sentiment_score - 0.5) * 2  # 0-1范围
        except Exception:
            # 使用简单关键词分析
            signal = self._keyword_analysis(news_text)
            response = f"基于关键词分析: {signal}"
            confidence = 0.5
        
        return AnalysisResult(
            agent_name=self.name,
            signal=signal,
            confidence=confidence,
            reasoning=response,
            indicators={"news_count": len(news_items)},
            risks=["新闻可能有滞后性", "市场情绪可能快速变化"]
        )
    
    def _analyze_sentiment(self, text: str) -> float:
        """分析情感分数 0-1"""
        positive_words = ["增长", "超预期", "突破", "利好", "beat", "growth", "surge"]
        negative_words = ["下滑", "miss", "诉讼", "裁员", "下调", "decline", "crash"]
        
        text_lower = text.lower()
        pos = sum(1 for w in positive_words if w in text_lower)
        neg = sum(1 for w in negative_words if w in text_lower)
        
        if pos > neg:
            return 0.7
        elif neg > pos:
            return 0.3
        return 0.5
    
    def _extract_signal(self, text: str) -> str:
        """提取交易信号"""
        text_upper = text.upper()
        if "BUY" in text_upper:
            return "BUY"
        elif "SELL" in text_upper:
            return "SELL"
        return "HOLD"
    
    def _keyword_analysis(self, news_text: str) -> str:
        """基于关键词的简单分析"""
        positive = ["beat", "growth", "surge", "rally", "upgrade"]
        negative = ["miss", "decline", "crash", "downgrade", "lawsuit"]
        
        text_lower = news_text.lower()
        pos_count = sum(1 for p in positive if p in text_lower)
        neg_count = sum(1 for n in negative if n in text_lower)
        
        if pos_count > neg_count:
            return "BUY"
        elif neg_count > pos_count:
            return "SELL"
        return "HOLD"
