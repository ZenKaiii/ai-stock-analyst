"""
RSS新闻抓取模块
"""
import feedparser
import re
from typing import List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    """新闻条目数据类"""
    title: str
    link: str
    published: datetime
    summary: str
    source: str
    symbol: Optional[str] = None


class RSSFetcher:
    """RSS新闻抓取器"""
    
    # 默认RSS源配置
    DEFAULT_SOURCES = {
        "seeking_alpha": {
            "url": "https://seekingalpha.com/feed.xml",
            "name": "Seeking Alpha",
            "priority": 1
        },
        "marketwatch": {
            "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
            "name": "MarketWatch",
            "priority": 2
        },
        "cnbc": {
            "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
            "name": "CNBC",
            "priority": 3
        },
        "investing": {
            "url": "https://www.investing.com/rss/news.rss",
            "name": "Investing.com",
            "priority": 4
        },
        "nasdaq": {
            "url": "https://www.nasdaq.com/feed/rssoutbound?category=Stocks",
            "name": "Nasdaq",
            "priority": 5
        }
    }
    
    def __init__(self):
        self.session = None
    
    def fetch_feed(self, url: str, source_name: str = "unknown") -> List[NewsItem]:
        """
        抓取单个RSS源
        
        Args:
            url: RSS feed URL
            source_name: 来源名称
            
        Returns:
            List[NewsItem]: 新闻列表
        """
        try:
            logger.info(f"Fetching RSS: {source_name}")
            feed = feedparser.parse(url)
            
            items = []
            for entry in feed.entries[:20]:  # 只取最近20条
                published = self._parse_date(entry)
                
                # 跳过过期新闻（超过3天）
                if published and published < datetime.now() - timedelta(days=3):
                    continue
                
                item = NewsItem(
                    title=entry.get("title", ""),
                    link=entry.get("link", ""),
                    published=published or datetime.now(),
                    summary=self._clean_html(entry.get("summary", "")),
                    source=source_name
                )
                items.append(item)
            
            logger.info(f"Fetched {len(items)} items from {source_name}")
            return items
            
        except Exception as e:
            logger.error(f"Error fetching RSS {url}: {e}")
            return []
    
    def fetch_all(self) -> List[NewsItem]:
        """抓取所有默认RSS源"""
        all_news = []
        
        for source_id, config in self.DEFAULT_SOURCES.items():
            news = self.fetch_feed(config["url"], config["name"])
            all_news.extend(news)
        
        # 按时间排序
        all_news.sort(key=lambda x: x.published, reverse=True)
        return all_news
    
    def fetch_by_symbol(self, symbol: str) -> List[NewsItem]:
        """
        抓取特定股票相关的新闻
        
        Args:
            symbol: 股票代码，如 AAPL
            
        Returns:
            List[NewsItem]: 相关新闻列表
        """
        all_news = []
        
        # Seeking Alpha 有股票特定feed
        sa_url = f"https://seekingalpha.com/api/sa/combined/{symbol}.xml"
        news = self.fetch_feed(sa_url, f"Seeking Alpha - {symbol}")
        for item in news:
            item.symbol = symbol
        all_news.extend(news)
        
        # 从通用源过滤
        general_news = self.fetch_all()
        for item in general_news:
            if symbol.upper() in item.title.upper():
                item.symbol = symbol
                all_news.append(item)
        
        # 去重并排序
        seen = set()
        unique_news = []
        for item in sorted(all_news, key=lambda x: x.published, reverse=True):
            key = f"{item.title[:50]}_{item.source}"
            if key not in seen:
                seen.add(key)
                unique_news.append(item)
        
        return unique_news[:20]
    
    def _parse_date(self, entry) -> Optional[datetime]:
        """解析RSS日期"""
        try:
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                import time
                return datetime.fromtimestamp(time.mktime(entry.published_parsed))
        except:
            pass
        return datetime.now()
    
    def _clean_html(self, html: str) -> str:
        """清理HTML标签"""
        clean = re.sub("<.*?>", "", html)
        return clean.strip()[:500]


# 便捷函数
def fetch_news(symbol: Optional[str] = None) -> List[NewsItem]:
    """
    获取新闻的便捷函数
    
    Args:
        symbol: 股票代码，为None则获取所有新闻
        
    Returns:
        List[NewsItem]: 新闻列表
    """
    fetcher = RSSFetcher()
    if symbol:
        return fetcher.fetch_by_symbol(symbol)
    return fetcher.fetch_all()
