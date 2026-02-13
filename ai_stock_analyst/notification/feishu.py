"""
飞书通知器
"""
import os
import requests
import json
import logging
from .base import BaseNotifier

logger = logging.getLogger(__name__)


class FeishuNotifier(BaseNotifier):
    """飞书机器人通知器"""
    
    def __init__(self):
        super().__init__("Feishu")
        self.webhook_url = os.getenv('FEISHU_WEBHOOK_URL', '')
    
    def is_configured(self) -> bool:
        return bool(self.webhook_url)
    
    def send(self, title: str, content: str, **kwargs) -> bool:
        if not self.is_configured():
            logger.warning("Feishu not configured")
            return False
        
        try:
            message = {
                "msg_type": "interactive",
                "card": {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": title
                        },
                        "template": kwargs.get('template', 'blue')
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": content
                            }
                        }
                    ]
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
            if result.get('code') == 0:
                logger.info("Feishu notification sent successfully")
                return True
            else:
                logger.error(f"Feishu API error: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Feishu notification: {e}")
            return False
    
    def send_text(self, content: str) -> bool:
        """发送文本消息"""
        if not self.is_configured():
            return False
        
        try:
            message = {
                "msg_type": "text",
                "content": {
                    "text": content
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
            
            return response.json().get('code') == 0
            
        except Exception as e:
            logger.error(f"Failed to send Feishu text: {e}")
            return False
