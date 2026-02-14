import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional

import feedparser
import requests

from ai_stock_analyst.rss.models import NewsItem
from ai_stock_analyst.rss.providers import EarningsCalendarProvider, GeopoliticalRiskProvider

logger = logging.getLogger(__name__)


class RSSFetcher:
    DEFAULT_SOURCES = {
        "seeking_alpha": {
            "url": "https://seekingalpha.com/feed.xml",
            "name": "Seeking Alpha",
            "priority": 1,
        },
        "marketwatch": {
            "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
            "name": "MarketWatch",
            "priority": 2,
        },
        "cnbc": {
            "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
            "name": "CNBC",
            "priority": 3,
        },
        "wsj": {
            "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
            "name": "WSJ",
            "priority": 4,
        },
        "yahoo_finance": {
            "url": "https://finance.yahoo.com/news/rssindex",
            "name": "Yahoo Finance",
            "priority": 5,
        },
        "google_stocks": {
            "url": "https://news.google.com/rss/search?q=stock+market&hl=en-US&gl=US&ceid=US:en",
            "name": "Google News Stocks",
            "priority": 6,
        },
        "fed_press": {
            "url": "https://www.federalreserve.gov/feeds/press_all.xml",
            "name": "Federal Reserve",
            "priority": 7,
        },
        "sec_press": {
            "url": "https://www.sec.gov/news/pressreleases.rss",
            "name": "SEC Press Releases",
            "priority": 8,
        },
        "sec_speeches": {
            "url": "https://www.sec.gov/news/speeches-statements.rss",
            "name": "SEC Speeches",
            "priority": 9,
        },
        "cftc_press": {
            "url": "https://www.cftc.gov/PressRoom/PressReleases/rss.xml",
            "name": "CFTC Press Releases",
            "priority": 10,
        },
        "imf_news": {
            "url": "https://www.imf.org/en/News/RSS",
            "name": "IMF News",
            "priority": 11,
        },
    }

    def __init__(self):
        self.structured_providers = [
            EarningsCalendarProvider(),
            GeopoliticalRiskProvider(),
        ]

    def fetch_feed(self, url: str, source_name: str = "unknown", timeout: int = 10) -> List[NewsItem]:
        try:
            logger.info(f"Fetching RSS: {source_name}")

            response = requests.get(
                url,
                timeout=timeout,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"
                    )
                },
            )
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            items: List[NewsItem] = []
            for entry in feed.entries[:25]:
                published = self._parse_date(entry)

                if published and published < datetime.now() - timedelta(days=5):
                    continue

                item = NewsItem(
                    title=entry.get("title", ""),
                    link=entry.get("link", ""),
                    published=published or datetime.now(),
                    summary=self._clean_html(entry.get("summary", "")),
                    source=source_name,
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
        all_news: List[NewsItem] = []

        for _, config in self.DEFAULT_SOURCES.items():
            news = self.fetch_feed(config["url"], config["name"])
            all_news.extend(news)

        for provider in self.structured_providers:
            try:
                all_news.extend(provider.fetch(self.fetch_feed))
            except Exception as e:
                logger.warning(f"Structured provider {provider.name} failed: {e}")

        return self._deduplicate(all_news)

    def fetch_by_symbol(self, symbol: str) -> List[NewsItem]:
        all_news: List[NewsItem] = []

        sa_url = f"https://seekingalpha.com/api/sa/combined/{symbol}.xml"
        sa_news = self.fetch_feed(sa_url, f"Seeking Alpha - {symbol}")
        for item in sa_news:
            item.symbol = symbol
        all_news.extend(sa_news)

        general_news = self.fetch_all()
        symbol_upper = symbol.upper()
        for item in general_news:
            title_upper = item.title.upper()
            if symbol_upper in title_upper or f"${symbol_upper}" in title_upper:
                item.symbol = symbol
                all_news.append(item)

        for provider in self.structured_providers:
            try:
                all_news.extend(provider.fetch(self.fetch_feed, symbol=symbol))
            except Exception as e:
                logger.warning(f"Structured provider {provider.name} failed for {symbol}: {e}")

        return self._deduplicate(all_news)[:30]

    def _deduplicate(self, items: List[NewsItem]) -> List[NewsItem]:
        seen = set()
        unique_news: List[NewsItem] = []

        for item in sorted(items, key=lambda x: x.published, reverse=True):
            key = f"{item.source}|{item.title.strip().lower()[:120]}"
            if key in seen:
                continue
            seen.add(key)
            unique_news.append(item)

        return unique_news

    def _parse_date(self, entry) -> Optional[datetime]:
        try:
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                import time

                return datetime.fromtimestamp(time.mktime(entry.published_parsed))
            if hasattr(entry, "updated_parsed") and entry.updated_parsed:
                import time

                return datetime.fromtimestamp(time.mktime(entry.updated_parsed))
        except Exception:
            return datetime.now()
        return datetime.now()

    def _clean_html(self, html: str) -> str:
        clean = re.sub("<.*?>", "", html)
        return clean.strip()[:500]


def fetch_news(symbol: Optional[str] = None) -> List[NewsItem]:
    fetcher = RSSFetcher()
    if symbol:
        return fetcher.fetch_by_symbol(symbol)
    return fetcher.fetch_all()
