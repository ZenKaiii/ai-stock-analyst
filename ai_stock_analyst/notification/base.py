"""
通知模块基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


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
    
    def format_stock_message(self, analysis_result: Dict[str, Any]) -> str:
        """
        格式化股票分析结果消息
        
        Args:
            analysis_result: 分析结果字典
            
        Returns:
            str: 格式化后的消息
        """
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
        
        agent_sections = []
        for analysis in analyses:
            agent_name = analysis.get('agent', '')
            agent_signal = analysis.get('signal', 'HOLD')
            agent_confidence = round(analysis.get('confidence', 0) * 100, 1)
            reasoning = analysis.get('reasoning', '')
            
            if agent_name == 'TechnicalAnalyst':
                section_title = '📊 技术面分析'
            elif agent_name == 'NewsAnalyst':
                section_title = '📰 新闻舆情'
            elif agent_name == 'SocialMediaAnalyst':
                section_title = '💬 社媒情绪'
            else:
                section_title = f'🤖 {agent_name}'
            
            key_points = self._extract_key_points(reasoning, max_lines=3)
            
            agent_sections.append(f"""
{section_title}
信号: {agent_signal} | 置信度: {agent_confidence}%
{key_points}
""")
        
        news_section = ""
        if news:
            news_lines = []
            for item in news[:3]:
                title = item.get('title', '')
                source = item.get('source', 'Unknown')
                if title:
                    news_lines.append(f"• [{source}] {title[:60]}{'...' if len(title) > 60 else ''}")
            if news_lines:
                news_section = f"""
📢 最新动态
""" + "\n".join(news_lines)
        
        message = f"""🎯 {symbol} 决策仪表盘

{signal_emoji} **{symbol}** | 信号: {signal} | 置信度: {confidence}%
💰 入场: ${decision.get('entry_price', 'N/A')} | 止损: ${decision.get('stop_loss', 'N/A')} | 目标: ${decision.get('target_price', 'N/A')}
{news_section}
{''.join(agent_sections)}

📋 综合决策
{decision.get('rationale', '无')}

---
AI Stock Analyzer
"""
        return message
    
    def _extract_key_points(self, reasoning: str, max_lines: int = 3) -> str:
        if not reasoning:
            return "暂无分析详情"
        
        lines = []
        for line in reasoning.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                line = line.replace('**', '').replace('*', '')
                lines.append(line)
            if len(lines) >= max_lines:
                break
        
        if not lines:
            return reasoning[:150] + '...' if len(reasoning) > 150 else reasoning
        
        return '\n'.join(f"  • {line[:80]}{'...' if len(line) > 80 else ''}" for line in lines)
