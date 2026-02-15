"""
主程序入口 - CLI
"""
import argparse
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any

from ai_stock_analyst.config import get_settings
from ai_stock_analyst.database import get_db
from ai_stock_analyst.data import fetch_stock_price
from ai_stock_analyst.rss import fetch_news, fetch_social
from ai_stock_analyst.agents import analyze_stock
from ai_stock_analyst.agents.recommendation import scan_for_opportunities
from ai_stock_analyst.agents.portfolio_analysis import analyze_portfolio, add_holding, get_holdings
from ai_stock_analyst.broker import fetch_ibkr_positions
from ai_stock_analyst.notification import get_notification_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI Stock Analyzer")
    parser.add_argument("--stocks", type=str, help="Comma-separated stock symbols")
    parser.add_argument("--type", type=str, default="full", choices=["quick", "full", "deep"])
    parser.add_argument("--no-notify", action="store_true", help="Disable notifications")
    parser.add_argument("--discover", action="store_true", help="Discover trending stocks from news")
    parser.add_argument("--discover-universe-size", type=int, default=0, help="Discovery: max universe size (0=all)")
    parser.add_argument("--discover-prefilter-size", type=int, default=120, help="Discovery: prefilter size")
    parser.add_argument("--discover-final-size", type=int, default=21, help="Discovery: final recommendation size")
    parser.add_argument("--discover-max-news", type=int, default=180, help="Discovery: max news items")
    parser.add_argument("--portfolio", action="store_true", help="Analyze portfolio holdings")
    parser.add_argument("--add-holding", type=str, help="Add holding: SYMBOL,SHARES,COST")
    parser.add_argument("--list-holdings", action="store_true", help="List all holdings")
    parser.add_argument("--sync-ibkr-holdings", action="store_true", help="Sync holdings from IBKR TWS/Gateway")
    parser.add_argument("--ibkr-check", action="store_true", help="Check IBKR connectivity/auth and print summary")
    parser.add_argument("--strict-ibkr", action="store_true", help="Exit non-zero if IBKR sync fails")
    
    args = parser.parse_args()
    
    if args.add_holding:
        parts = args.add_holding.split(",")
        if len(parts) != 3:
            print("Usage: --add-holding SYMBOL,SHARES,COST")
            return
        symbol, shares, cost = parts[0].strip().upper(), float(parts[1]), float(parts[2])
        add_holding(symbol, shares, cost)
        print(f"Added: {symbol} - {shares} shares @ ${cost}")
        return
    
    if args.list_holdings:
        holdings = get_holdings()
        if not holdings:
            print("No holdings found. Add holdings with --add-holding SYMBOL,SHARES,COST")
            return
        print(f"\n{'Symbol':<8} {'Shares':<10} {'Avg Cost':<12} {'Current':<12} {'Value':<14} {'P/L':<12}")
        print("-" * 70)
        for h in holdings:
            print(f"{h.get('symbol', ''):<8} {h.get('shares', 0):<10.2f} ${h.get('avg_cost', 0):<11.2f} ${h.get('current_price', 0):<11.2f} ${h.get('market_value', 0):<13.2f} ${h.get('unrealized_pnl', 0):<11.2f}")
        return

    if args.ibkr_check:
        mode = os.getenv("IBKR_API_MODE", "auto")
        print(f"IBKR mode: {mode}")
        if mode.lower() in {"cpapi", "auto"}:
            print(f"CPAPI base: {os.getenv('IBKR_CPAPI_BASE_URL', 'https://localhost:5000/v1/api')}")
        if mode.lower() in {"socket", "auto"}:
            print(f"Socket endpoint: {os.getenv('IBKR_HOST', '127.0.0.1')}:{os.getenv('IBKR_PORT', '7497')}")
        try:
            ib_holdings = fetch_ibkr_positions()
            print(f"IBKR check success. Holdings fetched: {len(ib_holdings)}")
            for h in ib_holdings[:5]:
                print(f"- {h['symbol']}: {h['shares']} @ {h['avg_cost']}")
        except Exception as e:
            print(f"IBKR check failed: {e}")
            raise SystemExit(2)
        return

    if args.sync_ibkr_holdings:
        try:
            ib_holdings = fetch_ibkr_positions()
            if not ib_holdings:
                print("No holdings found from IBKR.")
                if not args.portfolio:
                    return

            for h in ib_holdings:
                add_holding(h["symbol"], float(h["shares"]), float(h["avg_cost"]), notes="synced-from-ibkr")

            print(f"Synced {len(ib_holdings)} holdings from IBKR.")
            for h in ib_holdings:
                print(f"- {h['symbol']}: {h['shares']} @ {h['avg_cost']}")
            if not args.portfolio:
                return
        except Exception as e:
            print(f"IBKR sync failed: {e}")
            if args.strict_ibkr:
                raise SystemExit(2)
            if not args.portfolio:
                return
    
    if args.discover:
        logger.info("Discovering trending stocks from news...")
        universe_size = 0 if args.discover_universe_size <= 0 else max(args.discover_universe_size, 200)
        result = scan_for_opportunities(
            max_news=max(args.discover_max_news, 50),
            universe_size=universe_size,
            prefilter_size=max(args.discover_prefilter_size, 30),
            final_size=max(args.discover_final_size, 5),
        )
        
        print("\n" + "="*50)
        print("📈 热门股票发现")
        print("="*50)

        stats = result.get("scan_stats", {})
        if stats:
            print(
                f"扫描: {stats.get('scanned_universe', 0)} | "
                f"预筛: {stats.get('prefiltered', 0)} | "
                f"评分: {stats.get('scored', 0)} | "
                f"最终: {stats.get('final_count', 0)}"
            )
        
        if result.get("recommendations"):
            for idx, rec in enumerate(result["recommendations"], start=1):
                emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(rec["signal"], "⚪")
                company = rec.get("company_name", rec["symbol"])
                sector = rec.get("sector", "未知板块")
                print(
                    f"{idx:>2}. {emoji} {rec['symbol']:<6} ({company}) | 板块: {sector} | 信号: {rec['signal']:<5} | "
                    f"综合: {rec.get('score_100', rec.get('composite_score', 0)*100):.1f}/100 | 新闻: {rec['news_count']}"
                )
        
        print("\n" + result.get("summary", ""))
        
        if not args.no_notify:
            notify_mgr = get_notification_manager()
            notify_mgr.send("📈 热门股票发现", result.get("summary", ""))
        
        return
    
    if args.portfolio:
        logger.info("Analyzing portfolio...")
        holdings = get_holdings()
        
        if not holdings:
            print("No holdings found. Add holdings with --add-holding SYMBOL,SHARES,COST")
            return
        
        portfolio_data = [
            {
                "symbol": h["symbol"],
                "shares": h["shares"],
                "avg_cost": h["avg_cost"]
            }
            for h in holdings
        ]
        
        result = analyze_portfolio(portfolio_data)
        
        print("\n" + "="*50)
        print("📊 持仓分析报告")
        print("="*50)
        print(result.get("analysis", ""))
        
        if not args.no_notify:
            notify_mgr = get_notification_manager()
            notify_mgr.send("📊 持仓分析报告", result.get("analysis", ""))
        
        return
    settings = get_settings()
    stocks = args.stocks.split(",") if args.stocks else settings.stocks
    
    notify_mgr = get_notification_manager()
    status = notify_mgr.get_status()
    configured_channels = [k for k, v in status.items() if v]
    
    logger.info(f"Starting analysis for: {stocks}")
    logger.info(f"Configured notification channels: {configured_channels}")
    
    results = []
    
    for symbol in stocks:
        symbol = symbol.strip().upper()
        logger.info(f"\nAnalyzing {symbol}...")
        
        try:
            price_data = fetch_stock_price(symbol)
            if "error" in price_data:
                logger.error(f"Failed to fetch {symbol}: {price_data['error']}")
                continue
            
            logger.info(f"  Price: ${price_data.get('current_price', 0)}")
            
            news = fetch_news(symbol)
            social_data = fetch_social(symbol)
            
            analysis_data = {
                'symbol': symbol,
                'price_data': price_data,
                'news': [
                    {
                        'title': n.title,
                        'source': n.source,
                        'summary': n.summary,
                        'link': n.link,
                    }
                    for n in news[:10]
                ],
                'social_data': social_data
            }
            
            result = analyze_stock(symbol, analysis_data)
            results.append(result)
            
            signal = result['decision']['signal']
            logger.info(f"  Signal: {signal}")
            
            save_price_data(price_data)
            save_analysis_result(result)
            
            if not args.no_notify and configured_channels:
                notify_mgr.send_stock_analysis(result)
            
        except Exception as e:
            logger.error(f"Error: {e}")
            continue
    
    if not args.no_notify and len(results) > 1 and configured_channels:
        notify_mgr.send_batch_analysis(results)
    
    logger.info(f"\nAnalysis complete! Processed {len(results)} stocks.")


def save_price_data(data: dict):
    """保存价格数据到数据库"""
    try:
        db = get_db()
        query = """
            INSERT INTO stock_prices 
            (symbol, price, change, change_percent, volume, pe_ratio, market_cap, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """
        db.execute(query, (
            data["symbol"],
            data.get("current_price", 0),
            data.get("change", 0),
            data.get("change_percent", 0),
            data.get("volume", 0),
            data.get("pe_ratio", 0),
            data.get("market_cap", 0)
        ))
    except Exception as e:
        logger.error(f"Error saving data: {e}")


def save_analysis_result(result: dict):
    """保存分析结果到数据库"""
    try:
        db = get_db()
        decision = result.get('decision', {})
        query = """
            INSERT INTO analysis_results 
            (symbol, signal, confidence, summary, entry_price, stop_loss, target_price, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """
        db.execute(query, (
            result.get('symbol'),
            decision.get('signal'),
            decision.get('confidence', 0) / 100,
            decision.get('rationale', '')[:500],
            decision.get('entry_price'),
            decision.get('stop_loss'),
            decision.get('target_price')
        ))
    except Exception as e:
        logger.error(f"Error saving analysis: {e}")


if __name__ == "__main__":
    main()
