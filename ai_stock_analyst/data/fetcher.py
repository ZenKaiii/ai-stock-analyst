"""
股票数据获取模块
"""
import yfinance as yf
import logging
from typing import Dict
from ai_stock_analyst.data.features import calculate_features

logger = logging.getLogger(__name__)


def fetch_stock_price(symbol: str) -> Dict:
    """获取股票实时价格数据"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        # Fetch 6 months of data for anomaly detection (Z-scores)
        hist = ticker.history(period="6mo")
        
        features = calculate_features(hist)
        
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
            "ma5": features.get("ma5", 0),
            "ma20": features.get("ma20", 0),
            "trend": features.get("trend", "NEUTRAL"),
            "rsi14": features.get("rsi14", 50),
            "macd": features.get("macd", 0),
            "macd_signal": features.get("macd_signal", 0),
            "macd_hist": features.get("macd_hist", 0),
            "atr14": features.get("atr14", 0),
            "atr_pct": features.get("atr_pct", 0),
            "volatility_20d": features.get("volatility_20d", 0),
            "data_quality": features.get("data_quality", 0),
            "history": hist  # Return full history DataFrame for agents to use
        }
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}
