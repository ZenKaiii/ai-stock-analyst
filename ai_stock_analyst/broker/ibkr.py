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


def _fetch_with_cpapi(account: Optional[str]) -> List[Dict]:
    import requests

    base_url = _read_str(None, "IBKR_CPAPI_BASE_URL", "https://localhost:5000/v1/api").rstrip("/")
    verify_ssl = _read_bool(None, "IBKR_CPAPI_VERIFY_SSL", False)
    timeout = _read_int(None, "IBKR_CPAPI_TIMEOUT", 12)
    cookie = _read_str(None, "IBKR_CPAPI_COOKIE", "")

    session = requests.Session()
    if cookie:
        session.headers.update({"Cookie": cookie})

    # Keep the gateway session warm and ensure we have an authenticated context.
    try:
        session.get(f"{base_url}/tickle", timeout=timeout, verify=verify_ssl)
    except Exception:
        pass

    auth_resp = session.get(f"{base_url}/iserver/auth/status", timeout=timeout, verify=verify_ssl)
    auth_resp.raise_for_status()
    auth_json = auth_resp.json() if auth_resp.content else {}
    if not bool(auth_json.get("authenticated", False)):
        raise RuntimeError(
            "CPAPI session is not authenticated. Please login to Client Portal Gateway "
            "in browser and keep the session active."
        )

    accounts = _cpapi_list_accounts(session, base_url, timeout, verify_ssl)
    if not accounts:
        raise RuntimeError("CPAPI returned no accounts. Check IBKR account permissions.")

    account_id = account or accounts[0]
    if account and account not in accounts:
        raise RuntimeError(f"Configured IBKR_ACCOUNT={account} not found in CPAPI accounts: {accounts}")

    positions = _cpapi_get_positions(session, base_url, account_id, timeout, verify_ssl)
    holdings = []
    for item in positions:
        symbol = str(item.get("ticker") or item.get("symbol") or item.get("contractDesc") or "").strip()
        if not symbol:
            continue
        shares = item.get("position", item.get("size", 0))
        avg_cost = item.get("avgCost", item.get("avgPrice", item.get("cost", 0)))
        currency = str(item.get("currency") or "USD")
        holdings.append(_to_holding(symbol=symbol, shares=shares, avg_cost=avg_cost, currency=currency))
    return holdings


def _cpapi_list_accounts(session, base_url: str, timeout: int, verify_ssl: bool) -> List[str]:
    candidates: List[str] = []
    endpoints = [f"{base_url}/portfolio/accounts", f"{base_url}/iserver/accounts"]
    for endpoint in endpoints:
        try:
            resp = session.get(endpoint, timeout=timeout, verify=verify_ssl)
            if resp.status_code >= 400:
                continue
            payload = resp.json() if resp.content else []
            candidates.extend(_extract_accounts_from_payload(payload))
        except Exception:
            continue

    seen = set()
    out = []
    for acc in candidates:
        acc = str(acc).strip()
        if not acc or acc in seen:
            continue
        seen.add(acc)
        out.append(acc)
    return out


def _extract_accounts_from_payload(payload) -> List[str]:
    out: List[str] = []
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                for key in ("id", "accountId", "account_id", "account", "acctId"):
                    if item.get(key):
                        out.append(str(item.get(key)))
                        break
    elif isinstance(payload, dict):
        for key in ("accounts", "accountIds"):
            value = payload.get(key)
            if isinstance(value, list):
                out.extend(str(v) for v in value if v)
        for key in ("id", "accountId", "account_id", "account", "acctId"):
            if payload.get(key):
                out.append(str(payload.get(key)))
    return out


def _cpapi_get_positions(session, base_url: str, account_id: str, timeout: int, verify_ssl: bool):
    endpoints = [
        f"{base_url}/portfolio/{account_id}/positions/0",
        f"{base_url}/portfolio/{account_id}/positions",
    ]
    for endpoint in endpoints:
        try:
            resp = session.get(endpoint, timeout=timeout, verify=verify_ssl)
            if resp.status_code >= 400:
                continue
            payload = resp.json() if resp.content else []
            rows = _extract_positions_from_payload(payload)
            if rows is not None:
                return rows
        except Exception:
            continue
    raise RuntimeError("CPAPI positions endpoint returned no data. Check account and session state.")


def _extract_positions_from_payload(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("positions"), list):
            return payload.get("positions")
        if isinstance(payload.get("data"), list):
            return payload.get("data")
    return None


def fetch_ibkr_positions(
    host: Optional[str] = None,
    port: Optional[int] = None,
    client_id: Optional[int] = None,
    account: Optional[str] = None,
) -> List[Dict]:
    """从 IBKR 拉取持仓（Socket API 或 CPAPI）。

    Env fallback:
    - IBKR_API_MODE (auto/socket/cpapi, default auto)
    - IBKR_HOST (default 127.0.0.1)
    - IBKR_PORT (default 7497)
    - IBKR_CLIENT_ID (default 21)
    - IBKR_ACCOUNT (optional)
    - IBKR_CPAPI_BASE_URL (default https://localhost:5000/v1/api)
    - IBKR_CPAPI_VERIFY_SSL (default false)
    - IBKR_CPAPI_TIMEOUT (default 12)
    """
    mode = _read_str(None, "IBKR_API_MODE", "auto").lower()
    host = _read_str(host, "IBKR_HOST", "127.0.0.1")
    port = _read_int(port, "IBKR_PORT", 7497)
    client_id = _read_int(client_id, "IBKR_CLIENT_ID", 21)
    account = _read_str(account, "IBKR_ACCOUNT", "") or None

    fetchers = []
    if mode in {"socket", "tws"}:
        fetchers = ["ib_async", "ib_insync"]
    elif mode in {"cpapi", "web", "portal"}:
        fetchers = ["cpapi"]
    else:
        fetchers = ["ib_async", "ib_insync", "cpapi"]

    errors = []
    for fetcher_name in fetchers:
        try:
            if fetcher_name == "ib_async":
                return _fetch_with_ib_async(host, port, client_id, account)
            if fetcher_name == "ib_insync":
                return _fetch_with_ib_insync(host, port, client_id, account)
            if fetcher_name == "cpapi":
                return _fetch_with_cpapi(account)
        except Exception as e:
            errors.append(f"{fetcher_name}: {e}")

    raise RuntimeError(
        "Unable to fetch IBKR positions. "
        "For Socket mode, install `ib_async` (recommended) or `ib_insync` and ensure "
        "TWS/Gateway API is reachable. "
        "For CPAPI mode, ensure Client Portal Gateway is running and authenticated. "
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


def _read_bool(value: Optional[bool], env_key: str, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    env_val = os.getenv(env_key, "").strip().lower()
    if not env_val:
        return default
    return env_val in {"1", "true", "yes", "on"}
