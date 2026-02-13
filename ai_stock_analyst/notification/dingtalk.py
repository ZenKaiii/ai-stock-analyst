"""
钉钉通知器
"""
import os
import requests
import json
import logging
from .base import BaseNotifier

logger = logging.getLogger(__name__)


class DingTalkNotifier(BaseNotifier):
    """钉钉机器人通知器"""
    
    def __init__(self):
        super().__init__("DingTalk")
        self.webhook_url = os.getenv('DINGTALK_WEBHOOK_URL', '')
        self.secret = os.getenv('DINGTALK_SECRET', '')
    
    def is_configured(self) -> bool:
        return bool(self.webhook_url)
    
    def send(self, title: str, content: str, **kwargs) -> bool:
        if not self.is_configured():
            logger.warning("DingTalk not configured")
            return False
        
        try:
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": f"## {title}\n\n{content}"
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(message),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('errcode') == 0:
                logger.info("DingTalk notification sent successfully")
                return True
            else:
                logger.error(f"DingTalk API error: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send DingTalk notification: {e}")
            return False
    
    def send_text(self, content: str, at_all: bool = False) -> bool:
        """发送文本消息"""
        if not self.is_configured():
            return False
        
        try:
            message = {
                "msgtype": "text",
                "text": {
                    "content": content
                },
                "at": {
                    "isAtAll": at_all
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(message),
                timeout=30
            )
            response.raise_for_status()
            
            return response.json().get('errcode') == 0
            
        except Exception as e:
            logger.error(f"Failed to send DingTalk text: {e}")
            return False
