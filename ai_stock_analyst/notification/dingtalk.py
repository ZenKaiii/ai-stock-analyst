"""
钉钉通知器
"""
import os
import requests
import json
import logging
import re
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
            text_content = self._format_text_for_dingtalk(title, content)
            parts = self._split_text(text_content, max_len=1800)
            headers = {'Content-Type': 'application/json'}

            for idx, part in enumerate(parts):
                message = {
                    "msgtype": "text",
                    "text": {"content": part}
                }
                response = requests.post(
                    self.webhook_url,
                    headers=headers,
                    data=json.dumps(message),
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                if result.get('errcode') != 0:
                    logger.error(f"DingTalk API error: {result}")
                    return False
                logger.info(f"DingTalk notification sent successfully ({idx + 1}/{len(parts)})")
            return True
                
        except Exception as e:
            logger.error(f"Failed to send DingTalk notification: {e}")
            return False

    def _format_text_for_dingtalk(self, title: str, content: str) -> str:
        """钉钉移动端对 markdown 支持有限，统一转为易读纯文本。"""
        text = (content or "").replace("\r\n", "\n")
        text = text.replace("---", "\n")
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        text = text.replace("**", "").replace("`", "")
        text = re.sub(r"^[ \t]*\*\s+", "- ", text, flags=re.MULTILINE)
        text = re.sub(r"^[ \t]*•\s*", "- ", text, flags=re.MULTILINE)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

        return f"{title}\n\n{text}"

    def _split_text(self, text: str, max_len: int = 1800):
        if len(text) <= max_len:
            return [text]
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + max_len, len(text))
            split_pos = text.rfind("\n", start, end)
            if split_pos <= start:
                split_pos = end
            chunks.append(text[start:split_pos].strip())
            start = split_pos
        return [c for c in chunks if c]
    
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
