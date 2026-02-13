"""
持仓分析Agent - 分析用户持仓并提供建议
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

from ai_stock_analyst.agents.base import BaseAgent, AnalysisResult
from ai_stock_analyst.data import fetch_stock_price

logger = logging.getLogger(__name__)


@dataclass
class Holding:
    """持仓"""
    symbol: str
    shares: float
    avg_cost: float
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    unrealized_pnl_percent: Optional[float] = None


class PortfolioAnalyzer(BaseAgent):
    """持仓分析Agent"""
    
    def __init__(self):
        super().__init__("PortfolioAnalyzer")
    
    def analyze(self, data: Dict) -> AnalysisResult:
        """
        分析用户持仓
        
        Args:
            data: 包含持仓信息的字典
            
        Returns:
            AnalysisResult: 持仓分析结果
        """
        holdings = data.get("holdings", [])
        
        if not holdings:
            return AnalysisResult(
                agent_name=self.name,
                signal="HOLD",
                confidence=0.0,
                reasoning="没有持仓数据",
                indicators={},
                risks=["请先添加持仓"]
            )
        
        # 更新实时价格
        updated_holdings = self._update_prices(holdings)
        
        # 计算整体指标
        total_value = sum(h.market_value for h in updated_holdings if h.market_value)
        total_cost = sum(h.shares * h.avg_cost for h in updated_holdings)
        total_pnl = total_value - total_cost
        pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        # 分类持仓
        winners = [h for h in updated_holdings if h.unrealized_pnl_percent and h.unrealized_pnl_percent > 0]
        losers = [h for h in updated_holdings if h.unrealized_pnl_percent and h.unrealized_pnl_percent < 0]
        
        # 生成建议
        suggestions = self._generate_suggestions(updated_holdings, winners, losers)
        
        reasoning = self._build_analysis_text(
            updated_holdings, total_value, total_pnl, pnl_percent,
            winners, losers, suggestions
        )
        
        # 决定整体信号
        if len(winners) > len(losers) and pnl_percent > 5:
            signal = "BUY"
            confidence = 0.7
        elif len(losers) > len(winners) or pnl_percent < -5:
            signal = "SELL"
            confidence = 0.7
        else:
            signal = "HOLD"
            confidence = 0.5
        
        return AnalysisResult(
            agent_name=self.name,
            signal=signal,
            confidence=confidence,
            reasoning=reasoning,
            indicators={
                "total_value": round(total_value, 2),
                "total_pnl": round(total_pnl, 2),
                "pnl_percent": round(pnl_percent, 2),
                "holdings_count": len(updated_holdings),
                "winners_count": len(winners),
                "losers_count": len(losers),
                "holdings": [
                    {
                        "symbol": h.symbol,
                        "shares": h.shares,
                        "avg_cost": h.avg_cost,
                        "current_price": h.current_price,
                        "market_value": round(h.market_value, 2) if h.market_value else 0,
                        "unrealized_pnl": round(h.unrealized_pnl, 2) if h.unrealized_pnl else 0,
                        "unrealized_pnl_percent": round(h.unrealized_pnl_percent, 2) if h.unrealized_pnl_percent else 0
                    }
                    for h in updated_holdings
                ]
            },
            risks=self._analyze_risks(updated_holdings, winners, losers)
        )
    
    def _update_prices(self, holdings: List[Dict]) -> List[Holding]:
        """更新持仓的实时价格"""
        updated = []
        
        for h in holdings:
            symbol = h.get("symbol", "")
            shares = h.get("shares", 0)
            avg_cost = h.get("avg_cost", 0)
            
            holding = Holding(
                symbol=symbol,
                shares=shares,
                avg_cost=avg_cost
            )
            
            # 获取实时价格
            try:
                price_data = fetch_stock_price(symbol)
                if "error" not in price_data:
                    holding.current_price = price_data.get("current_price")
                    if holding.current_price:
                        holding.market_value = holding.current_price * shares
                        holding.unrealized_pnl = (holding.current_price - avg_cost) * shares
                        holding.unrealized_pnl_percent = (
                            (holding.current_price - avg_cost) / avg_cost * 100
                            if avg_cost > 0 else 0
                        )
            except Exception as e:
                logger.warning(f"Failed to fetch price for {symbol}: {e}")
            
            updated.append(holding)
        
        return updated
    
    def _generate_suggestions(self, holdings: List[Holding], winners: List[Holding], losers: List[Holding]) -> List[str]:
        """生成操作建议"""
        suggestions = []
        
        # 盈利最多的建议持有或部分卖出
        if winners:
            best = max(winners, key=lambda h: h.unrealized_pnl_percent or 0)
            if best.unrealized_pnl_percent and best.unrealized_pnl_percent > 20:
                suggestions.append(f"考虑部分卖出 {best.symbol}，锁定利润（+{best.unrealized_pnl_percent:.1f}%）")
            else:
                suggestions.append(f"持有 {best.symbol}，当前盈利 +{best.unrealized_pnl_percent:.1f}%")
        
        # 亏损最多的建议止损或加仓
        if losers:
            worst = min(losers, key=lambda h: h.unrealized_pnl_percent or 0)
            if worst.unrealized_pnl_percent and worst.unrealized_pnl_percent < -15:
                suggestions.append(f"关注 {worst.symbol}，亏损 {-worst.unrealized_pnl_percent:.1f}%，考虑止损或加仓摊平")
            else:
                suggestions.append(f"持有 {worst.symbol}，当前亏损 {worst.unrealized_pnl_percent:.1f}%")
        
        # 多元化建议
        if len(holdings) < 3:
            suggestions.append("持仓过于集中，建议分散投资")
        elif len(holdings) > 10:
            suggestions.append("持仓数量较多，建议检视并精简")
        
        return suggestions
    
    def _build_analysis_text(self, holdings: List[Holding], total_value: float, 
                           total_pnl: float, pnl_percent: float,
                           winners: List[Holding], losers: List[Holding],
                           suggestions: List[str]) -> str:
        """构建分析文本"""
        lines = ["📊 持仓分析报告\n"]
        
        # 总览
        pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
        lines.append(f"总市值: ${total_value:,.2f}")
        lines.append(f"{pnl_emoji} 总盈亏: ${total_pnl:,.2f} ({pnl_percent:+.2f}%)")
        lines.append(f"持仓数量: {len(holdings)} 只")
        lines.append(f"盈利: {len(winners)} 只 | 亏损: {len(losers)} 只")
        
        # 持仓明细
        lines.append("\n📈 持仓明细:")
        for h in sorted(holdings, key=lambda x: x.unrealized_pnl_percent or 0, reverse=True):
            pnl_emoji = "🟢" if (h.unrealized_pnl or 0) >= 0 else "🔴"
            pnl_str = f"{pnl_emoji} {h.symbol}: {h.shares}股 @ ${h.avg_cost:.2f} = ${h.market_value:.2f}"
            if h.unrealized_pnl_percent is not None:
                pnl_str += f" ({h.unrealized_pnl_percent:+.2f}%)"
            lines.append(pnl_str)
        
        # 建议
        if suggestions:
            lines.append("\n💡 操作建议:")
            for s in suggestions:
                lines.append(f"  • {s}")
        
        return "\n".join(lines)
    
    def _analyze_risks(self, holdings: List[Holding], winners: List[Holding], losers: List[Holding]) -> List[str]:
        """分析风险"""
        risks = []
        
        # 过度集中
        if holdings:
            max_holding = max(holdings, key=lambda h: h.market_value or 0)
            if max_holding.market_value:
                total_value = sum(h.market_value for h in holdings if h.market_value)
                concentration = (max_holding.market_value / total_value * 100) if total_value > 0 else 0
                if concentration > 40:
                    risks.append(f"{max_holding.symbol} 占比 {concentration:.1f}%，过于集中")
        
        # 亏损过多
        if len(losers) > len(winners):
            risks.append("亏损股票多于盈利，需要关注")
        
        # 全部亏损
        if winners and len(winners) == 0:
            risks.append("全部持仓亏损，建议检视投资策略")
        
        return risks if risks else ["风险可控"]


def analyze_portfolio(portfolio_data: List[Dict]) -> Dict:
    """
    分析用户持仓
    
    Args:
        portfolio_data: 持仓列表，如 [{"symbol": "AAPL", "shares": 10, "avg_cost": 150}]
    
    Returns:
        Dict: 分析结果
    """
    logger.info(f"分析持仓: {len(portfolio_data)} 只股票")
    
    agent = PortfolioAnalyzer()
    data = {"holdings": portfolio_data}
    result = agent.analyze(data)
    
    return {
        "signal": result.signal,
        "confidence": result.confidence,
        "analysis": result.reasoning,
        "metrics": result.indicators,
        "risks": result.risks
    }


def add_holding(symbol: str, shares: float, avg_cost: float, notes: str = "") -> bool:
    """添加或更新持仓"""
    from ai_stock_analyst.database import get_db
    
    db = get_db()
    
    # 检查是否已存在
    existing = db.fetch_one(
        "SELECT id FROM portfolio_holdings WHERE symbol = ?",
        (symbol.upper(),)
    )
    
    if existing:
        db.execute(
            "UPDATE portfolio_holdings SET shares = ?, avg_cost = ?, notes = ?, updated_at = datetime('now') WHERE symbol = ?",
            (shares, avg_cost, notes, symbol.upper())
        )
    else:
        db.execute(
            "INSERT INTO portfolio_holdings (symbol, shares, avg_cost, notes) VALUES (?, ?, ?, ?)",
            (symbol.upper(), shares, avg_cost, notes)
        )
    
    logger.info(f"Added/Updated holding: {symbol} - {shares} shares @ ${avg_cost}")
    return True


def get_holdings() -> List[Dict]:
    """获取所有持仓"""
    from ai_stock_analyst.database import get_db
    
    db = get_db()
    holdings = db.fetch_all("SELECT * FROM portfolio_holdings ORDER BY symbol")
    
    return holdings or []
