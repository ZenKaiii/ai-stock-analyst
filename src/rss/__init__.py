"""
RSS包初始化

导出RSS相关类和函数
"""
from .feed import RSSFetcher, NewsItem, fetch_news
from .social import SocialMediaFetcher, fetch_social

__all__ = [
    "RSSFetcher", 
    "NewsItem", 
    "fetch_news",
    "SocialMediaFetcher", 
    "fetch_social"
]
