"""
社交媒体抓取模块（Twitter/X + Reddit）
"""
import feedparser
import re
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SocialMediaFetcher:
    """社交媒体抓取器"""
    
    # RSSHub多实例failover
    RSSHUB_URLS = [
        "https://rsshub.app",
        "https://rsshub.rssforever.com",
    ]
    
    # 股票相关Twitter账号
    TWITTER_ACCOUNTS = [
        "unusual_whales",
        "StockMKTNewz",
        "DeItaone",
        "FirstSquawk",
        "CNBCnow",
    ]
    
    def fetch_twitter_by_symbol(self, symbol: str, max_items: int = 50) -> List[Dict]:
        """
        通过RSSHub抓取Twitter股票讨论
        
        Args:
            symbol: 股票代码
            max_items: 最大条目数
            
        Returns:
            List[Dict]: 推文列表
        """
        results = []
        cashtag = f"${symbol.upper()}"
        
        for rsshub_url in self.RSSHUB_URLS:
            try:
                url = f"{rsshub_url}/twitter/keyword/{cashtag}"
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:max_items]:
                    results.append({
                        "platform": "twitter",
                        "author": entry.get("author", ""),
                        "content": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "published": self._parse_date(entry),
                        "symbol": symbol,
                        "likes": 0,
                        "retweets": 0
                    })
                
                if results:
                    break
                    
            except Exception as e:
                logger.warning(f"RSSHub {rsshub_url} failed: {e}")
                continue
        
        return results
    
    def fetch_reddit_by_symbol(self, symbol: str, max_items: int = 50) -> List[Dict]:
        """
        抓取Reddit股票讨论
        
        Args:
            symbol: 股票代码
            max_items: 最大条目数
            
        Returns:
            List[Dict]: 帖子列表
        """
        results = []
        subreddits = ["wallstreetbets", "stocks", "investing"]
        
        for subreddit in subreddits:
            try:
                # Reddit搜索RSS
                url = f"https://www.reddit.com/r/{subreddit}/search.rss?q={symbol}&restrict_sr=1"
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:max_items]:
                    results.append({
                        "platform": "reddit",
                        "author": entry.get("author", ""),
                        "content": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "published": self._parse_date(entry),
                        "symbol": symbol,
                        "subreddit": subreddit,
                        "score": 0,
                        "comments": 0
                    })
                    
            except Exception as e:
                logger.warning(f"Reddit r/{subreddit} failed: {e}")
                continue
        
        return results
    
    def fetch_by_symbol(self, symbol: str) -> Dict:
        """
        获取股票的所有社交媒体讨论
        
        Args:
            symbol: 股票代码
            
        Returns:
            Dict: 包含帖子列表和情感统计
        """
        twitter_posts = self.fetch_twitter_by_symbol(symbol)
        reddit_posts = self.fetch_reddit_by_symbol(symbol)
        
        all_posts = twitter_posts + reddit_posts
        sentiment = self._analyze_sentiment(all_posts)
        
        return {
            "posts": all_posts,
            "sentiment": sentiment,
            "twitter_count": len(twitter_posts),
            "reddit_count": len(reddit_posts),
            "total": len(all_posts)
        }
    
    def _analyze_sentiment(self, posts: List[Dict]) -> Dict:
        """
        简单情感分析
        
        Args:
            posts: 帖子列表
            
        Returns:
            Dict: 情感统计
        """
        bullish_keywords = [
            "buy", "long", "bull", "moon", "rocket", "🚀", "💰", 
            "calls", "up", "surge", "rally", "breakout"
        ]
        bearish_keywords = [
            "sell", "short", "bear", "crash", "dump", "tank", 
            "puts", "down", "bearish"
        ]
        
        bullish = 0
        bearish = 0
        
        for post in posts:
            text = post.get("content", "").lower()
            b_score = sum(1 for k in bullish_keywords if k in text)
            br_score = sum(1 for k in bearish_keywords if k in text)
            
            if b_score > br_score:
                bullish += 1
            elif br_score > b_score:
                bearish += 1
        
        total = len(posts) if posts else 1
        return {
            "bullish": bullish,
            "bearish": bearish,
            "neutral": len(posts) - bullish - bearish,
            "bullish_pct": round(bullish / total * 100, 1),
            "bearish_pct": round(bearish / total * 100, 1)
        }
    
    def _parse_date(self, entry) -> Optional[datetime]:
        """解析日期"""
        try:
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                import time
                return datetime.fromtimestamp(time.mktime(entry.published_parsed))
        except:
            pass
        return datetime.now()


# 便捷函数
def fetch_social(symbol: str) -> Dict:
    """
    获取社交媒体讨论的便捷函数
    
    Args:
        symbol: 股票代码
        
    Returns:
        Dict: 社交媒体数据
    """
    fetcher = SocialMediaFetcher()
    return fetcher.fetch_by_symbol(symbol)
