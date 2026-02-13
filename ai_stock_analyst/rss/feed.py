import feedparser
import re
import requests
import socket
from typing import List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    title: str
    link: str
    published: datetime
    summary: str
    source: str
    symbol: Optional[str] = None


class RSSFetcher:
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
    
    def fetch_feed(self, url: str, source_name: str = "unknown", timeout: int = 10) -> List[NewsItem]:
        try:
            logger.info(f"Fetching RSS: {source_name}")
            
            response = requests.get(url, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            items = []
            for entry in feed.entries[:20]:
                published = self._parse_date(entry)
                
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
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching RSS from {source_name} ({url}), skipping")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching RSS {source_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching RSS {source_name}: {e}")
            return []
    
    def fetch_all(self) -> List[NewsItem]:
        all_news = []
        
        for source_id, config in self.DEFAULT_SOURCES.items():
            news = self.fetch_feed(config["url"], config["name"])
            all_news.extend(news)
        
        all_news.sort(key=lambda x: x.published, reverse=True)
        return all_news
    
    def fetch_by_symbol(self, symbol: str) -> List[NewsItem]:
        all_news = []
        
        sa_url = f"https://seekingalpha.com/api/sa/combined/{symbol}.xml"
        news = self.fetch_feed(sa_url, f"Seeking Alpha - {symbol}")
        for item in news:
            item.symbol = symbol
        all_news.extend(news)
        
        general_news = self.fetch_all()
        for item in general_news:
            if symbol.upper() in item.title.upper():
                item.symbol = symbol
                all_news.append(item)
        
        seen = set()
        unique_news = []
        for item in sorted(all_news, key=lambda x: x.published, reverse=True):
            key = f"{item.title[:50]}_{item.source}"
            if key not in seen:
                seen.add(key)
                unique_news.append(item)
        
        return unique_news[:20]
    
    def _parse_date(self, entry) -> Optional[datetime]:
        try:
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                import time
                return datetime.fromtimestamp(time.mktime(entry.published_parsed))
        except:
            pass
        return datetime.now()
    
    def _clean_html(self, html: str) -> str:
        clean = re.sub("<.*?>", "", html)
        return clean.strip()[:500]


def fetch_news(symbol: Optional[str] = None) -> List[NewsItem]:
    fetcher = RSSFetcher()
    if symbol:
        return fetcher.fetch_by_symbol(symbol)
    return fetcher.fetch_all()
