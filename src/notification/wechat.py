"""
企业微信通知器
"""
import os
import requests
import json
import logging
from .base import BaseNotifier

logger = logging.getLogger(__name__)


class WeChatWorkNotifier(BaseNotifier):
    """企业微信机器人通知器"""
    
    def __init__(self):
        super().__init__("WeChat Work")
        self.webhook_url = os.getenv('WECHAT_WORK_WEBHOOK_URL', '')
    
    def is_configured(self) -> bool:
        return bool(self.webhook_url)
    
    def send(self, title: str, content: str, **kwargs) -> bool:
        if not self.is_configured():
            logger.warning("WeChat Work not configured")
            return False
        
        try:
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"**{title}**\n\n{content}"
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
                logger.info("WeChat Work notification sent successfully")
                return True
            else:
                logger.error(f"WeChat Work API error: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send WeChat Work notification: {e}")
            return False
    
    def send_text(self, content: str, mentioned_list: list = None) -> bool:
        """发送文本消息"""
        if not self.is_configured():
            return False
        
        try:
            message = {
                "msgtype": "text",
                "text": {
                    "content": content,
                    "mentioned_list": mentioned_list or []
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
            logger.error(f"Failed to send WeChat Work text: {e}")
            return False
    
    def send_news(self, title: str, description: str, url: str, pic_url: str = "") -> bool:
        """发送图文消息"""
        if not self.is_configured():
            return False
        
        try:
            message = {
                "msgtype": "news",
                "news": {
                    "articles": [
                        {
                            "title": title,
                            "description": description,
                            "url": url,
                            "picurl": pic_url
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
            
            return response.json().get('errcode') == 0
            
        except Exception as e:
            logger.error(f"Failed to send WeChat Work news: {e}")
            return False
