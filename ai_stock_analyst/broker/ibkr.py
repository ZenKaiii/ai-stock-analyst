"""IBKR 持仓读取（可选依赖：ib_async 或 ib_insync）"""
from __future__ import annotations

import os
from typing import Dict, List, Optional


def _to_holding(symbol: str, shares: float, avg_cost: float, currency: str = "USD") -> Dict:
    return {
        "symbol": symbol.upper(),
        "shares": float(shares),
        "avg_cost": float(avg_cost),
        "currency": currency,
    }


def _fetch_with_ib_async(host: str, port: int, client_id: int, account: Optional[str]) -> List[Dict]:
    from ib_async import IB

    ib = IB()
    ib.connect(host, port, clientId=client_id, readonly=True, timeout=12)
    try:
        positions = ib.positions()
        holdings = []
        for p in positions:
            if account and getattr(p, "account", None) != account:
                continue
            symbol = getattr(getattr(p, "contract", None), "symbol", "")
            if not symbol:
                continue
            holdings.append(
                _to_holding(
                    symbol=symbol,
                    shares=getattr(p, "position", 0),
                    avg_cost=getattr(p, "avgCost", 0),
                    currency=getattr(getattr(p, "contract", None), "currency", "USD"),
                )
            )
        return holdings
    finally:
        ib.disconnect()


def _fetch_with_ib_insync(host: str, port: int, client_id: int, account: Optional[str]) -> List[Dict]:
    from ib_insync import IB

    ib = IB()
    ib.connect(host, port, clientId=client_id, readonly=True, timeout=12)
    try:
        positions = ib.positions()
        holdings = []
        for p in positions:
            if account and getattr(p, "account", None) != account:
                continue
            symbol = getattr(getattr(p, "contract", None), "symbol", "")
            if not symbol:
                continue
            holdings.append(
                _to_holding(
                    symbol=symbol,
                    shares=getattr(p, "position", 0),
                    avg_cost=getattr(p, "avgCost", 0),
                    currency=getattr(getattr(p, "contract", None), "currency", "USD"),
                )
            )
        return holdings
    finally:
        ib.disconnect()


def fetch_ibkr_positions(
    host: Optional[str] = None,
    port: Optional[int] = None,
    client_id: Optional[int] = None,
    account: Optional[str] = None,
) -> List[Dict]:
    """从 IBKR TWS/Gateway 拉取持仓。

    Env fallback:
    - IBKR_HOST (default 127.0.0.1)
    - IBKR_PORT (default 7497)
    - IBKR_CLIENT_ID (default 21)
    - IBKR_ACCOUNT (optional)
    """
    host = _read_str(host, "IBKR_HOST", "127.0.0.1")
    port = _read_int(port, "IBKR_PORT", 7497)
    client_id = _read_int(client_id, "IBKR_CLIENT_ID", 21)
    account = _read_str(account, "IBKR_ACCOUNT", "") or None

    errors = []
    for fetcher in (_fetch_with_ib_async, _fetch_with_ib_insync):
        try:
            return fetcher(host, port, client_id, account)
        except Exception as e:
            errors.append(f"{fetcher.__name__}: {e}")

    raise RuntimeError(
        "Unable to fetch IBKR positions. Install `ib_async` (recommended) "
        "or `ib_insync`, and ensure TWS/Gateway API is reachable. "
        f"Details: {' | '.join(errors)}"
    )


def _read_str(value: Optional[str], env_key: str, default: str) -> str:
    if value is not None and str(value).strip():
        return str(value).strip()
    env_val = os.getenv(env_key, "").strip()
    return env_val if env_val else default


def _read_int(value: Optional[int], env_key: str, default: int) -> int:
    if value is not None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
    env_val = os.getenv(env_key, "").strip()
    if not env_val:
        return default
    try:
        return int(env_val)
    except ValueError:
        return default
