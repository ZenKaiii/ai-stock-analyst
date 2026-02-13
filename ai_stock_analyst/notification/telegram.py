"""
Telegram通知器
"""
import os
import requests
import logging
from .base import BaseNotifier

logger = logging.getLogger(__name__)


class TelegramNotifier(BaseNotifier):
    """Telegram Bot通知器"""
    
    def __init__(self):
        super().__init__("Telegram")
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)
    
    def send(self, title: str, content: str, **kwargs) -> bool:
        if not self.is_configured():
            logger.warning("Telegram not configured")
            return False
        
        try:
            message = f"**{title}**\n\n{content}"
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Telegram notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    def send_photo(self, title: str, image_path: str, caption: str = "") -> bool:
        """发送图片通知"""
        if not self.is_configured():
            return False
        
        try:
            url = f"{self.base_url}/sendPhoto"
            
            with open(image_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': self.chat_id,
                    'caption': f"**{title}**\n\n{caption}" if caption else title,
                    'parse_mode': 'Markdown'
                }
                
                response = requests.post(url, files=files, data=data, timeout=30)
                response.raise_for_status()
                
                logger.info(f"Telegram photo sent successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send Telegram photo: {e}")
            return False
