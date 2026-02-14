"""
股票数据获取模块
"""
import yfinance as yf
import logging
from datetime import datetime, timedelta
from typing import Dict
from ai_stock_analyst.data.features import calculate_features

logger = logging.getLogger(__name__)
_market_context_cache = {"expires_at": datetime.min, "value": {}}


def fetch_market_context() -> Dict:
    """获取市场风险上下文（QQQ + VIX），带短时缓存。"""
    try:
        now = datetime.utcnow()
        if _market_context_cache["value"] and now < _market_context_cache["expires_at"]:
            return _market_context_cache["value"]

        qqq = yf.Ticker("QQQ").history(period="3mo")
        vix = yf.Ticker("^VIX").history(period="3mo")

        qqq_close = qqq["Close"].dropna() if not qqq.empty else None
        vix_close = vix["Close"].dropna() if not vix.empty else None

        qqq_price = float(qqq_close.iloc[-1]) if qqq_close is not None and not qqq_close.empty else 0.0
        qqq_ma20 = float(qqq_close.tail(20).mean()) if qqq_close is not None and len(qqq_close) >= 20 else 0.0
        qqq_ret_5d = (
            ((float(qqq_close.iloc[-1]) / float(qqq_close.iloc[-6])) - 1) * 100
            if qqq_close is not None and len(qqq_close) >= 6
            else 0.0
        )
        vix_level = float(vix_close.iloc[-1]) if vix_close is not None and not vix_close.empty else 0.0

        qqq_risk = "LOW"
        if qqq_price and qqq_ma20 and qqq_price < qqq_ma20 and qqq_ret_5d < -2:
            qqq_risk = "HIGH"
        elif qqq_price and qqq_ma20 and (qqq_price < qqq_ma20 or qqq_ret_5d < -1):
            qqq_risk = "MEDIUM"

        vix_risk = "LOW"
        if vix_level >= 24:
            vix_risk = "HIGH"
        elif vix_level >= 20:
            vix_risk = "MEDIUM"

        context = {
            "qqq_price": round(qqq_price, 2),
            "qqq_ma20": round(qqq_ma20, 2),
            "qqq_ret_5d": round(qqq_ret_5d, 2),
            "qqq_risk": qqq_risk,
            "vix_level": round(vix_level, 2),
            "vix_risk": vix_risk,
        }
        _market_context_cache["value"] = context
        _market_context_cache["expires_at"] = now + timedelta(minutes=20)
        return context
    except Exception as e:
        logger.warning(f"Failed to fetch market context: {e}")
        return {}


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
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "business_summary": (info.get("longBusinessSummary", "") or "")[:260],
            "current_price": round(current, 2),
            "previous_close": round(previous, 2),
            "change": round(current - previous, 2),
            "change_percent": round((current / previous - 1) * 100, 2) if previous else 0,
            "volume": info.get("volume", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "market_cap": info.get("marketCap", 0),
            "trailing_eps": info.get("trailingEps", 0),
            "forward_eps": info.get("forwardEps", 0),
            "revenue_growth": info.get("revenueGrowth", 0),
            "earnings_growth": info.get("earningsGrowth", 0),
            "profit_margins": info.get("profitMargins", 0),
            "operating_margins": info.get("operatingMargins", 0),
            "return_on_equity": info.get("returnOnEquity", 0),
            "debt_to_equity": info.get("debtToEquity", 0),
            "current_ratio": info.get("currentRatio", 0),
            "quick_ratio": info.get("quickRatio", 0),
            "free_cashflow": info.get("freeCashflow", 0),
            "total_cash": info.get("totalCash", 0),
            "total_debt": info.get("totalDebt", 0),
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
            "market_context": fetch_market_context(),
            "history": hist  # Return full history DataFrame for agents to use
        }
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}
