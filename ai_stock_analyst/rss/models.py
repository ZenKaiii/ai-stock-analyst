from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class NewsItem:
    title: str
    link: str
    published: datetime
    summary: str
    source: str
    symbol: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
