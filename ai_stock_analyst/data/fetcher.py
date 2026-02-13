"""
股票数据获取模块
"""
import yfinance as yf
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def fetch_stock_price(symbol: str) -> Dict:
    """获取股票实时价格数据"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1mo")
        
        # 计算均线
        ma5 = ma20 = 0
        trend = "NEUTRAL"
        if not hist.empty:
            ma5 = hist["Close"].tail(5).mean()
            ma20 = hist["Close"].tail(20).mean()
            trend = "BULLISH" if ma5 > ma20 else "BEARISH"
        
        current = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        previous = info.get("previousClose", 1)
        
        return {
            "symbol": symbol,
            "name": info.get("longName", symbol),
            "current_price": round(current, 2),
            "previous_close": round(previous, 2),
            "change": round(current - previous, 2),
            "change_percent": round((current / previous - 1) * 100, 2) if previous else 0,
            "volume": info.get("volume", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "market_cap": info.get("marketCap", 0),
            "ma5": round(ma5, 2),
            "ma20": round(ma20, 2),
            "trend": trend
        }
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}
