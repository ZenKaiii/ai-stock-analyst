"""
技术指标与风险特征计算
"""
from __future__ import annotations

from typing import Dict

import pandas as pd


def _safe_float(value: float | int | None, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_rsi(close: pd.Series, period: int = 14) -> float:
    if close is None or len(close) < period + 1:
        return 50.0

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    latest_gain = _safe_float(avg_gain.iloc[-1], 0.0)
    latest_loss = _safe_float(avg_loss.iloc[-1], 0.0)

    if latest_loss == 0:
        return 100.0 if latest_gain > 0 else 50.0

    rs = latest_gain / latest_loss
    rsi = 100 - (100 / (1 + rs))
    return round(float(rsi), 2)


def calculate_macd(close: pd.Series) -> Dict[str, float]:
    if close is None or len(close) < 35:
        return {"macd": 0.0, "macd_signal": 0.0, "macd_hist": 0.0}

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    hist = macd_line - signal_line

    return {
        "macd": round(_safe_float(macd_line.iloc[-1]), 4),
        "macd_signal": round(_safe_float(signal_line.iloc[-1]), 4),
        "macd_hist": round(_safe_float(hist.iloc[-1]), 4),
    }


def calculate_atr(history: pd.DataFrame, period: int = 14) -> float:
    if history is None or history.empty or len(history) < period + 1:
        return 0.0

    high = history["High"]
    low = history["Low"]
    close = history["Close"]

    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr = tr.rolling(window=period).mean()
    return round(_safe_float(atr.iloc[-1]), 4)


def calculate_features(history: pd.DataFrame) -> Dict[str, float | str]:
    """从历史K线计算技术与风险特征。"""
    if history is None or history.empty:
        return {
            "ma5": 0.0,
            "ma20": 0.0,
            "trend": "NEUTRAL",
            "rsi14": 50.0,
            "macd": 0.0,
            "macd_signal": 0.0,
            "macd_hist": 0.0,
            "atr14": 0.0,
            "atr_pct": 0.0,
            "volatility_20d": 0.0,
            "data_quality": 0.0,
        }

    close = history["Close"]
    ma5 = _safe_float(close.tail(5).mean()) if len(close) >= 5 else _safe_float(close.mean())
    ma20 = _safe_float(close.tail(20).mean()) if len(close) >= 20 else _safe_float(close.mean())
    trend = "BULLISH" if ma5 > ma20 else "BEARISH"

    rsi14 = calculate_rsi(close, period=14)
    macd_metrics = calculate_macd(close)
    atr14 = calculate_atr(history, period=14)

    current_price = _safe_float(close.iloc[-1], 0.0)
    atr_pct = round((atr14 / current_price) * 100, 3) if current_price > 0 else 0.0

    returns = close.pct_change().dropna()
    volatility_20d = 0.0
    if len(returns) >= 20:
        volatility_20d = round(_safe_float(returns.tail(20).std()) * 100, 3)

    expected_cols = ["Open", "High", "Low", "Close", "Volume"]
    completeness = sum(1 for col in expected_cols if col in history.columns) / len(expected_cols)
    freshness = 1.0 if len(history) >= 20 else min(len(history) / 20, 1.0)
    data_quality = round((completeness * 0.6 + freshness * 0.4), 3)

    return {
        "ma5": round(ma5, 2),
        "ma20": round(ma20, 2),
        "trend": trend,
        "rsi14": rsi14,
        **macd_metrics,
        "atr14": atr14,
        "atr_pct": atr_pct,
        "volatility_20d": volatility_20d,
        "data_quality": data_quality,
    }
