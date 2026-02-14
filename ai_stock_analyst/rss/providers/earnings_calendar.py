from __future__ import annotations

from typing import List

from ai_stock_analyst.rss.models import NewsItem
from ai_stock_analyst.rss.providers.base import (
    StructuredNewsProvider,
    build_google_news_url,
    mark_items,
)


class EarningsCalendarProvider(StructuredNewsProvider):
    name = "EarningsCalendarProvider"

    def fetch(self, fetch_feed, symbol: str | None = None) -> List[NewsItem]:
        if symbol:
            query = f"{symbol}+earnings+guidance+revenue+eps"
            items = fetch_feed(build_google_news_url(query), f"Earnings Watch - {symbol}", timeout=12)
            return mark_items(items, tag="earnings_event", symbol=symbol)

        query = "US+earnings+calendar+stocks"
        items = fetch_feed(build_google_news_url(query), "Earnings Watch", timeout=12)
        return mark_items(items, tag="earnings_event")
