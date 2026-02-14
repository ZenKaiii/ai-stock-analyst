"""
美股候选池加载与预筛
"""
from __future__ import annotations

import logging
import re
from typing import Dict, List, Tuple

import requests
import yfinance as yf

logger = logging.getLogger(__name__)

NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"
SYMBOL_PATTERN = re.compile(r"^[A-Z][A-Z\.\-]{0,5}$")

# Fallback universe in case network source is unavailable.
FALLBACK_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "AMD", "NFLX",
    "JPM", "BAC", "GS", "V", "MA", "WMT", "COST", "HD", "NKE", "SBUX",
    "UNH", "LLY", "JNJ", "PFE", "MRK", "XOM", "CVX", "COP", "CAT", "BA",
    "SPY", "QQQ", "IWM", "DIA", "TLT", "GLD", "SLV", "USO",
]


def load_us_equity_universe(max_symbols: int = 1800) -> List[str]:
    """加载美股候选池（NASDAQ Trader 官方符号目录）。"""
    symbols = set()
    symbols.update(_load_nasdaq_listed())
    symbols.update(_load_other_listed())

    cleaned = sorted(_normalize_symbol(s) for s in symbols if _is_valid_symbol(s))
    cleaned = [s for s in cleaned if s]
    if not cleaned:
        logger.warning("Failed to load NASDAQ Trader universe. Using fallback universe.")
        cleaned = FALLBACK_UNIVERSE.copy()
    return cleaned[:max_symbols]


def prefilter_universe(
    symbols: List[str],
    top_k: int = 120,
    min_price: float = 3.0,
    min_dollar_volume: float = 20_000_000,
) -> List[Dict]:
    """对候选池做轻量预筛（价格/流动性/动量）。"""
    if not symbols:
        return []

    chunk_size = 120
    prefiltered: List[Dict] = []

    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i : i + chunk_size]
        yf_symbols = [_to_yf_symbol(s) for s in chunk]
        try:
            raw = yf.download(
                tickers=" ".join(yf_symbols),
                period="3mo",
                interval="1d",
                auto_adjust=False,
                group_by="ticker",
                progress=False,
                threads=True,
            )
        except Exception as e:
            logger.warning(f"Prefilter download failed for chunk {i // chunk_size + 1}: {e}")
            continue

        for symbol in chunk:
            ysym = _to_yf_symbol(symbol)
            hist = _extract_hist(raw, ysym)
            if hist is None or hist.empty or len(hist) < 25:
                continue

            close = hist.get("Close")
            volume = hist.get("Volume")
            if close is None or volume is None:
                continue
            close = close.dropna()
            volume = volume.dropna()
            if close.empty or volume.empty or len(close) < 25 or len(volume) < 25:
                continue

            price = float(close.iloc[-1])
            avg_dollar_volume_20 = float((close.tail(20) * volume.tail(20)).mean())
            if price < min_price or avg_dollar_volume_20 < min_dollar_volume:
                continue

            ret20 = (float(close.iloc[-1]) / float(close.iloc[-21]) - 1) if len(close) >= 21 else 0.0
            ret5 = (float(close.iloc[-1]) / float(close.iloc[-6]) - 1) if len(close) >= 6 else 0.0
            vol20 = float(close.pct_change().dropna().tail(20).std() * 100) if len(close) >= 21 else 0.0

            score = (
                ret20 * 100 * 0.55
                + ret5 * 100 * 0.25
                + min(avg_dollar_volume_20 / 100_000_000, 10) * 0.20
                - max(vol20 - 4.5, 0) * 0.6
            )

            prefiltered.append(
                {
                    "symbol": symbol,
                    "price": round(price, 2),
                    "avg_dollar_volume_20": round(avg_dollar_volume_20, 2),
                    "ret20_pct": round(ret20 * 100, 2),
                    "ret5_pct": round(ret5 * 100, 2),
                    "vol20_pct": round(vol20, 2),
                    "prefilter_score": round(score, 4),
                }
            )

    prefiltered.sort(key=lambda x: x["prefilter_score"], reverse=True)
    return prefiltered[:top_k]


def _load_nasdaq_listed() -> List[str]:
    return _load_pipe_text_symbols(
        NASDAQ_LISTED_URL,
        symbol_keys=("Symbol",),
        extra_filter=lambda row: row.get("Test Issue", "N") == "N",
    )


def _load_other_listed() -> List[str]:
    return _load_pipe_text_symbols(
        OTHER_LISTED_URL,
        symbol_keys=("NASDAQ Symbol", "CQS Symbol", "ACT Symbol"),
        extra_filter=lambda row: row.get("Test Issue", "N") == "N",
    )


def _load_pipe_text_symbols(url: str, symbol_keys: Tuple[str, ...], extra_filter=None) -> List[str]:
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.warning(f"Failed to fetch universe source {url}: {e}")
        return []

    lines = [line.strip() for line in resp.text.splitlines() if line.strip()]
    if len(lines) < 2:
        return []

    header = lines[0].split("|")
    out = []
    for line in lines[1:]:
        if line.startswith("File Creation Time"):
            continue
        parts = line.split("|")
        if len(parts) != len(header):
            continue
        row = dict(zip(header, parts))
        if extra_filter and not extra_filter(row):
            continue
        symbol = ""
        for key in symbol_keys:
            if row.get(key):
                symbol = row.get(key, "").strip()
                if symbol:
                    break
        if symbol:
            out.append(symbol)
    return out


def _is_valid_symbol(symbol: str) -> bool:
    if not symbol:
        return False
    symbol = symbol.strip().upper()
    if any(c in symbol for c in ["$", "/", "^", "="]):
        return False
    return bool(SYMBOL_PATTERN.match(symbol))


def _normalize_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if "." in symbol:
        symbol = symbol.replace(".", "-")
    return symbol


def _to_yf_symbol(symbol: str) -> str:
    return symbol.replace(".", "-").upper()


def _extract_hist(raw, ysym: str):
    if raw is None or getattr(raw, "empty", True):
        return None

    # Multi ticker: level 0 is ticker when group_by=ticker
    if hasattr(raw, "columns") and getattr(raw.columns, "nlevels", 1) > 1:
        level0 = set(raw.columns.get_level_values(0))
        if ysym in level0:
            return raw[ysym]
        return None

    # Single ticker fallback
    return raw
