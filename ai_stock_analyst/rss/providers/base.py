from __future__ import annotations

import logging
from datetime import datetime
from typing import Callable, List

from ai_stock_analyst.rss.models import NewsItem

logger = logging.getLogger(__name__)

FetchFn = Callable[[str, str, int], List[NewsItem]]


class StructuredNewsProvider:
    name = "StructuredNewsProvider"

    def fetch(self, fetch_feed: FetchFn, symbol: str | None = None) -> List[NewsItem]:
        raise NotImplementedError


def build_google_news_url(query: str) -> str:
    return (
        "https://news.google.com/rss/search?q="
        f"{query}&hl=en-US&gl=US&ceid=US:en"
    )


def mark_items(items: List[NewsItem], tag: str, symbol: str | None = None) -> List[NewsItem]:
    for item in items:
        item.metadata["event_tag"] = tag
        if symbol:
            item.symbol = symbol
    return items


def utcnow() -> datetime:
    return datetime.utcnow()
