from __future__ import annotations

from typing import List

from ai_stock_analyst.rss.models import NewsItem
from ai_stock_analyst.rss.providers.base import (
    StructuredNewsProvider,
    build_google_news_url,
    mark_items,
)


class GeopoliticalRiskProvider(StructuredNewsProvider):
    name = "GeopoliticalRiskProvider"

    QUERIES = [
        ("geopolitical+risk+stock+market", "Geopolitical Risk Monitor"),
        ("Trump+tariffs+stocks+markets", "Trump Policy Watch"),
        ("US+China+trade+tension+stocks", "US-China Tension Watch"),
        ("Middle+East+oil+price+stock+market", "Energy Shock Watch"),
    ]

    def fetch(self, fetch_feed, symbol: str | None = None) -> List[NewsItem]:
        all_items: List[NewsItem] = []
        for query, source_name in self.QUERIES:
            items = fetch_feed(build_google_news_url(query), source_name, timeout=12)
            all_items.extend(mark_items(items, tag="geopolitics", symbol=symbol))
        return all_items
