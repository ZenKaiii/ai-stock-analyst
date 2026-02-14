#!/usr/bin/env python3
"""
最小可用回测脚本（日线）
- 策略: 趋势+动量(RSI/MACD) + 风险闸门(ATR/波动)
- 输出: Markdown + JSON 报告
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yfinance as yf

from ai_stock_analyst.data.features import calculate_features


@dataclass
class BacktestMetrics:
    symbol: str
    total_return_pct: float
    benchmark_return_pct: float
    max_drawdown_pct: float
    trades: int
    hit_rate_pct: float


def decide_signal(features: Dict) -> int:
    trend = features.get("trend", "NEUTRAL")
    rsi14 = float(features.get("rsi14", 50) or 50)
    macd = float(features.get("macd", 0) or 0)
    macd_signal = float(features.get("macd_signal", 0) or 0)
    atr_pct = float(features.get("atr_pct", 0) or 0)
    volatility_20d = float(features.get("volatility_20d", 0) or 0)

    signal = 0
    if trend == "BULLISH" and macd >= macd_signal and rsi14 < 72:
        signal = 1
    elif trend == "BEARISH" and (rsi14 > 78 or macd < macd_signal):
        signal = -1

    # Risk gate
    if signal == 1 and (atr_pct >= 4.0 or volatility_20d >= 3.0):
        signal = 0
    return signal


def run_backtest(symbol: str, period: str) -> BacktestMetrics:
    df = yf.download(symbol, period=period, interval="1d", auto_adjust=False, progress=False)
    if df.empty or len(df) < 80:
        return BacktestMetrics(symbol, 0.0, 0.0, 0.0, 0, 0.0)

    # yfinance may return MultiIndex columns; normalize to a Series.
    close = _extract_close_series(df)
    if close.empty or len(close) < 80:
        return BacktestMetrics(symbol, 0.0, 0.0, 0.0, 0, 0.0)

    df_norm = _normalize_ohlcv(df)
    if df_norm.empty:
        return BacktestMetrics(symbol, 0.0, 0.0, 0.0, 0, 0.0)

    max_len = min(len(df_norm), len(close))
    strategy_curve = [1.0]
    benchmark_curve = [1.0]
    trade_results: List[float] = []

    for i in range(40, max_len - 1):
        hist = df_norm.iloc[: i + 1]
        features = calculate_features(hist)
        signal = decide_signal(features)

        today = float(close.iloc[i])
        nxt = float(close.iloc[i + 1])
        next_ret = (nxt / today) - 1

        strat_ret = signal * next_ret
        strategy_curve.append(strategy_curve[-1] * (1 + strat_ret))
        benchmark_curve.append(benchmark_curve[-1] * (1 + next_ret))

        if signal != 0:
            trade_results.append(strat_ret)

    total_return_pct = (strategy_curve[-1] - 1) * 100
    benchmark_return_pct = (benchmark_curve[-1] - 1) * 100

    peak = strategy_curve[0]
    mdd = 0.0
    for v in strategy_curve:
        if v > peak:
            peak = v
        drawdown = (v - peak) / peak
        if drawdown < mdd:
            mdd = drawdown

    trades = len(trade_results)
    wins = sum(1 for r in trade_results if r > 0)
    hit_rate = (wins / trades * 100) if trades else 0.0

    return BacktestMetrics(
        symbol=symbol,
        total_return_pct=round(total_return_pct, 2),
        benchmark_return_pct=round(benchmark_return_pct, 2),
        max_drawdown_pct=round(mdd * 100, 2),
        trades=trades,
        hit_rate_pct=round(hit_rate, 2),
    )


def _extract_close_series(df: pd.DataFrame) -> pd.Series:
    if "Close" in df.columns:
        close = df["Close"]
    elif isinstance(df.columns, pd.MultiIndex):
        try:
            close = df.xs("Close", axis=1, level=0)
        except Exception:
            return pd.Series(dtype=float)
    else:
        return pd.Series(dtype=float)

    if isinstance(close, pd.DataFrame):
        if close.empty:
            return pd.Series(dtype=float)
        close = close.iloc[:, 0]
    return pd.to_numeric(close, errors="coerce").dropna()


def _normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()

    if isinstance(df.columns, pd.MultiIndex):
        out = pd.DataFrame(index=df.index)
        for field in ["Open", "High", "Low", "Close", "Volume"]:
            try:
                col = df.xs(field, axis=1, level=0)
                if isinstance(col, pd.DataFrame):
                    out[field] = pd.to_numeric(col.iloc[:, 0], errors="coerce")
                else:
                    out[field] = pd.to_numeric(col, errors="coerce")
            except Exception:
                out[field] = pd.NA
        return out.dropna(subset=["Close"])

    expected = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
    out = df[expected].copy()
    for c in expected:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out.dropna(subset=["Close"])


def write_reports(metrics: List[BacktestMetrics], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    md_path = output_dir / f"backtest_{ts}.md"
    json_path = output_dir / f"backtest_{ts}.json"

    lines = [
        "# Backtest Report",
        "",
        f"Generated at (UTC): {datetime.utcnow().isoformat()}",
        "",
        "| Symbol | Strategy Return | Benchmark Return | Max Drawdown | Trades | Hit Rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    json_payload = []
    for m in metrics:
        lines.append(
            f"| {m.symbol} | {m.total_return_pct:.2f}% | {m.benchmark_return_pct:.2f}% | "
            f"{m.max_drawdown_pct:.2f}% | {m.trades} | {m.hit_rate_pct:.2f}% |"
        )
        json_payload.append(m.__dict__)

    md_path.write_text("\n".join(lines), encoding="utf-8")
    json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return md_path


def main():
    parser = argparse.ArgumentParser(description="Run stock strategy backtest")
    parser.add_argument("--symbols", type=str, default="SPY,QQQ")
    parser.add_argument("--period", type=str, default="2y")
    parser.add_argument("--output-dir", type=str, default="reports")
    args = parser.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    metrics = [run_backtest(symbol, args.period) for symbol in symbols]
    report_path = write_reports(metrics, Path(args.output_dir))

    print(f"Backtest done: {report_path}")
    for item in metrics:
        print(
            f"{item.symbol}: strategy={item.total_return_pct:.2f}% benchmark={item.benchmark_return_pct:.2f}% "
            f"mdd={item.max_drawdown_pct:.2f}% trades={item.trades} hit={item.hit_rate_pct:.2f}%"
        )


if __name__ == "__main__":
    main()
