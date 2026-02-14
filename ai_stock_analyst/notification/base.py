"""
通知模块基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseNotifier(ABC):
    """通知器基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def is_configured(self) -> bool:
        """检查是否已配置"""
        pass
    
    @abstractmethod
    def send(self, title: str, content: str, **kwargs) -> bool:
        """
        发送通知
        
        Args:
            title: 通知标题
            content: 通知内容
            **kwargs: 额外参数
            
        Returns:
            bool: 是否发送成功
        """
        pass
    
    def _format_anomaly_alerts(self, analyses: List) -> str:
        alerts = []
        for a in analyses:
            if a.get('agent') == 'AnomalyAgent':
                anomalies = a.get('risks', [])
                if anomalies:
                    alerts.extend(anomalies)
        
        if not alerts:
            return ""
            
        return "⚠️ **市场异动监测**:\n" + "\n".join(f"*   {alert}" for alert in alerts)

    def _clean_bullet_line(self, line: str) -> str:
        if not line:
            return ""
        line = line.strip()
        while line and line[0] in {"•", "-", "*", "·"}:
            line = line[1:].strip()
        return line

    def format_stock_message(self, analysis_result: Dict[str, Any]) -> str:
        symbol = analysis_result.get('symbol', '')
        decision = analysis_result.get('decision', {})
        signal = decision.get('signal', 'HOLD')
        confidence = decision.get('confidence', 0)
        analyses = analysis_result.get('analyses', [])
        news = analysis_result.get('news', [])
        
        signal_emoji = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HOLD': '🟡'
        }.get(signal, '⚪')
        
        one_sentence = self._extract_one_sentence(decision.get('rationale', ''))
        risks = self._extract_risks(analyses)
        catalysts = self._extract_catalysts(analyses)
        macro = self._extract_agent_section(analyses, "MacroRegimeAgent", "🌍 宏观环境", 3)
        liquidity = self._extract_agent_section(analyses, "LiquidityQualityAgent", "💧 流动性质量", 3)
        fundamental = self._extract_agent_section(analyses, "FundamentalAnalyst", "🧾 财报与基本面", 3)
        anomaly_alerts = self._format_anomaly_alerts(analyses)
        news_summary = self._format_news_summary(news)
        tech_analysis = self._format_technical_analysis(analyses)
        checklist = self._generate_checklist(analyses, decision)
        score_100 = decision.get("score_100", 50)
        
        # Build Markdown message with better structure
        message = f"""# 🎯 {symbol} 决策仪表盘

---

### {signal_emoji} **{signal}** | 置信度: **{confidence}%**
> {one_sentence}
> 综合评分: **{score_100}/100**

---

#### 💰 关键点位
*   **建议入场**: `${decision.get('entry_price', 'N/A')}`
*   **止损价**: `${decision.get('stop_loss', 'N/A')}`
*   **目标价**: `${decision.get('target_price', 'N/A')}`
*   **建议仓位**: `{decision.get('position_size', '5-10%')}`

---

{news_summary}

---

{anomaly_alerts}

---

{tech_analysis}

---

{macro}

---

{liquidity}

---

{fundamental}

---

{risks}

---

{catalysts}

---

#### 📋 操作建议
*   **🆕 空仓者**: {"✨ 建议买入" if signal == "BUY" else "⏳ 观望等待" if signal == "HOLD" else "❌ 不建议买入"}
*   **💼 持仓者**: {"✅ 建议持有" if signal != "SELL" else "🚨 考虑卖出"}

---

{checklist}

---
*AI Stock Analyzer*
"""
        message = message.replace("\n\n\n", "\n").replace("---\n\n---", "---")
        return message

    def _extract_agent_section(self, analyses: List, agent_name: str, title: str, limit: int = 3) -> str:
        for a in analyses:
            if a.get("agent") != agent_name:
                continue
            lines = []
            for raw in str(a.get("reasoning", "")).splitlines():
                cleaned = self._clean_bullet_line(raw)
                if cleaned and len(cleaned) > 8:
                    lines.append(f"*   {cleaned[:120]}")
                if len(lines) >= limit:
                    break
            if lines:
                return title + "\n" + "\n".join(lines)
        return ""
    
    def _extract_one_sentence(self, rationale: str) -> str:
        if not rationale:
            return "需要更多分析"
        lines = [l.strip() for l in rationale.split('\n') if l.strip()]
        for line in lines:
            if '信号' in line or '建议' in line or '最终' in line:
                return line[:100]
        return lines[0][:100] if lines else "分析完成"
    
    def _format_news_summary(self, news: List) -> str:
        if not news:
            return ""
        lines = ["📰 重要信息速览"]
        for item in news[:4]:
            title = self._clean_bullet_line(item.get('title', '')[:70])
            summary = self._clean_bullet_line(item.get('summary', '')[:80])
            source = item.get('source', '来源未知')
            if title:
                if summary:
                    lines.append(f"• [{source}] {title} | 概要: {summary}")
                else:
                    lines.append(f"• [{source}] {title}")
        return '\n'.join(lines)
    
    def _format_technical_analysis(self, analyses: List) -> str:
        for a in analyses:
            if a.get('agent') == 'TechnicalAnalyst':
                reasoning = a.get('reasoning', '')
                lines = ["📊 技术面"]
                key_lines = []
                for line in reasoning.split('\n'):
                    line = self._clean_bullet_line(line)
                    if line and len(line) > 10 and len(key_lines) < 3:
                        line = line.replace('**', '')
                        key_lines.append(f"  • {line[:120]}")
                if key_lines:
                    lines.extend(key_lines)
                return '\n'.join(lines)
        return ""
    
    def _extract_risks(self, analyses: List) -> str:
        risk_keywords = ['风险', 'risk', '下跌', '下跌', '利空', '警告', '担忧']
        risks = []
        for a in analyses:
            reasoning = a.get('reasoning', '')
            for line in reasoning.split('\n'):
                line = self._clean_bullet_line(line)
                if any(kw in line.lower() for kw in risk_keywords) and len(line) > 20:
                    risks.append(f"• {line[:110]}")
                    if len(risks) >= 3:
                        break
        if risks:
            return "🚨 风险警报:\n" + '\n'.join(risks)
        return ""
    
    def _extract_catalysts(self, analyses: List) -> str:
        catalyst_keywords = ['利好', '上涨', '增长', '突破', '机会', '看涨', 'bullish']
        catalysts = []
        for a in analyses:
            reasoning = a.get('reasoning', '')
            for line in reasoning.split('\n'):
                line = self._clean_bullet_line(line)
                if any(kw in line.lower() for kw in catalyst_keywords) and len(line) > 20:
                    catalysts.append(f"• {line[:110]}")
                    if len(catalysts) >= 3:
                        break
        if catalysts:
            return "✨ 利好催化:\n" + '\n'.join(catalysts)
        return ""
    
    def _generate_checklist(self, analyses: List, decision: Dict) -> str:
        checks = []
        
        for a in analyses:
            if a.get('agent') == 'TechnicalAnalyst':
                reasoning = a.get('reasoning', '').lower()
                if '多头' in reasoning or 'bullish' in reasoning:
                    checks.append("✅ 多头排列")
                elif '空头' in reasoning or 'bearish' in reasoning:
                    checks.append("❌ 空头排列")
                else:
                    checks.append("⚠️ 趋势不明")
                break
        
        conf = decision.get('confidence', 0)
        if conf >= 70:
            checks.append(f"✅ 置信度 {conf}%")
        elif conf >= 50:
            checks.append(f"⚠️ 置信度 {conf}%")
        else:
            checks.append(f"❌ 置信度 {conf}%")
        
        if checks:
            return "✅ 检查清单:\n" + '\n'.join(f"  {c}" for c in checks)
        return ""
