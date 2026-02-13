"""
主程序入口 - CLI
"""
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any

from ai_stock_analyst.config import get_settings
from ai_stock_analyst.database import get_db
from ai_stock_analyst.data import fetch_stock_price
from ai_stock_analyst.rss import fetch_news, fetch_social
from ai_stock_analyst.agents import analyze_stock
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
    args = parser.parse_args()
    
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
                'news': [{'title': n.title, 'source': n.source} for n in news[:10]],
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
    return results


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
