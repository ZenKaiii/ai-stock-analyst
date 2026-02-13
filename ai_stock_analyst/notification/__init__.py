"""
通知模块

支持多种通知渠道：Telegram、钉钉、飞书、企业微信
"""
from .base import BaseNotifier
from .telegram import TelegramNotifier
from .dingtalk import DingTalkNotifier
from .feishu import FeishuNotifier
from .wechat import WeChatWorkNotifier
from .manager import NotificationManager, get_notification_manager

__all__ = [
    "BaseNotifier",
    "TelegramNotifier",
    "DingTalkNotifier",
    "FeishuNotifier",
    "WeChatWorkNotifier",
    "NotificationManager",
    "get_notification_manager",
]
