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
        
        signal_emoji = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HOLD': '🟡'
        }.get(signal, '⚪')
        
        message = f"""
{signal_emoji} **{symbol}** 分析结果

**信号**: {signal}
**置信度**: {confidence}%
**建议入场价**: ${decision.get('entry_price', 'N/A')}
**止损价**: ${decision.get('stop_loss', 'N/A')}
**目标价**: ${decision.get('target_price', 'N/A')}

**分析摘要**:
{decision.get('rationale', '无')[:200]}...

---
*AI Stock Analyzer*
"""
        return message
