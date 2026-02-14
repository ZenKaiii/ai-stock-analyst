"""
通知管理器 - 统一管理多个通知渠道
"""
import logging
from typing import List, Dict, Any, Optional
from .base import BaseNotifier
from .telegram import TelegramNotifier
from .dingtalk import DingTalkNotifier
from .feishu import FeishuNotifier
from .wechat import WeChatWorkNotifier

logger = logging.getLogger(__name__)


class NotificationManager:
    """通知管理器 - 支持多渠道同时推送"""
    
    def __init__(self):
        self.notifiers: List[BaseNotifier] = [
            TelegramNotifier(),
            DingTalkNotifier(),
            FeishuNotifier(),
            WeChatWorkNotifier(),
        ]
        self.enabled_notifiers: List[BaseNotifier] = []
        self._update_enabled_notifiers()
    
    def _update_enabled_notifiers(self):
        """更新已启用的通知器列表"""
        self.enabled_notifiers = [
            n for n in self.notifiers if n.is_configured()
        ]
        if self.enabled_notifiers:
            logger.info(f"Enabled notifiers: {[n.name for n in self.enabled_notifiers]}")
        else:
            logger.warning("No notifiers configured!")
    
    def get_status(self) -> Dict[str, bool]:
        """获取所有通知器的状态"""
        return {
            notifier.name: notifier.is_configured()
            for notifier in self.notifiers
        }
    
    def send(self, title: str, content: str, **kwargs) -> Dict[str, bool]:
        """
        发送通知到所有已配置的渠道
        
        Args:
            title: 通知标题
            content: 通知内容
            **kwargs: 额外参数
            
        Returns:
            Dict[str, bool]: 每个渠道的发送结果
        """
        self._update_enabled_notifiers()
        
        if not self.enabled_notifiers:
            logger.warning("No notifiers configured, skipping notification")
            return {}
        
        results = {}
        for notifier in self.enabled_notifiers:
            try:
                success = notifier.send(title, content, **kwargs)
                results[notifier.name] = success
                if success:
                    logger.info(f"Notification sent via {notifier.name}")
                else:
                    logger.error(f"Failed to send notification via {notifier.name}")
            except Exception as e:
                logger.error(f"Error sending notification via {notifier.name}: {e}")
                results[notifier.name] = False
        
        return results
    
    def send_stock_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, bool]:
        """
        发送股票分析结果通知
        
        Args:
            analysis_result: 分析结果字典
            
        Returns:
            Dict[str, bool]: 每个渠道的发送结果
        """
        self._update_enabled_notifiers()
        
        if not self.enabled_notifiers:
            logger.warning("No notifiers configured, skipping notification")
            return {}
        
        results = {}
        for notifier in self.enabled_notifiers:
            try:
                message = notifier.format_stock_message(analysis_result)
                title = f"📊 {analysis_result.get('symbol', 'Stock')} 决策卡"
                success = notifier.send(title, message)
                results[notifier.name] = success
            except Exception as e:
                logger.error(f"Error sending stock analysis via {notifier.name}: {e}")
                results[notifier.name] = False
        
        return results
    
    def send_batch_analysis(self, results: List[Dict[str, Any]]) -> Dict[str, bool]:
        if not results:
            return {}
        
        summary_lines = [
            f"# 📊 每日分析汇总报告\n",
            f"---",
            f"本次共分析了 **{len(results)}** 只股票：\n"
        ]
        
        for result in results:
            symbol = result.get('symbol', '')
            decision = result.get('decision', {})
            signal = decision.get('signal', 'HOLD')
            conf = decision.get('confidence', 0)
            
            emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡'}.get(signal, '⚪')
            summary_lines.append(f"*   {emoji} **{symbol}**: `{signal}` (置信度: {conf}%)")
        
        summary_lines.append("\n---\n*AI Stock Analyzer*")
        content = "\n".join(summary_lines)
        
        return self.send("📈 每日分析汇总报告", content)


# 全局通知管理器实例
_notification_manager = None


def get_notification_manager() -> NotificationManager:
    """获取通知管理器实例（单例模式）"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager
