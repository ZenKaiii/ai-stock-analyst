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
            markdown_text = self._format_markdown_for_dingtalk(title, content)
            parts = self._split_markdown(markdown_text, max_len=3500)
            headers = {'Content-Type': 'application/json'}

            for idx, part in enumerate(parts):
                message = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": title if len(parts) == 1 else f"{title} ({idx + 1}/{len(parts)})",
                        "text": part,
                    },
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

    def _format_markdown_for_dingtalk(self, title: str, content: str) -> str:
        """将通用 markdown 调整为钉钉更稳定的 markdown 形式。"""
        text = (content or "").replace("\r\n", "\n")
        # 去掉与 title 重复的首行标题
        text = re.sub(rf"^\s*#+\s*{re.escape(title)}\s*\n+", "", text, flags=re.IGNORECASE)
        text = text.replace("---", "\n\n---\n\n")
        text = re.sub(r"^[ \t]*•\s*", "- ", text, flags=re.MULTILINE)
        text = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", text)
        # 避免过深标题在钉钉端显示不稳定
        text = re.sub(r"^####\s+", "### ", text, flags=re.MULTILINE)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return f"## {title}\n\n{text}"

    def _split_markdown(self, text: str, max_len: int = 3500):
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

    def format_stock_message(self, analysis_result):
        symbol = analysis_result.get("symbol", "")
        decision = analysis_result.get("decision", {})
        analyses = analysis_result.get("analyses", [])
        news = analysis_result.get("news", [])

        signal = decision.get("signal", "HOLD")
        confidence = decision.get("confidence", 0)
        signal_icon = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal, "⚪")

        news_lines = []
        for idx, item in enumerate(news[:3], start=1):
            title = self._clean_bullet_line(item.get("title", ""))[:90]
            source = item.get("source", "Unknown")
            if title:
                news_lines.append(f"{idx}. **[{source}]** {title}")
        news_block = "\n".join(news_lines) if news_lines else "无重点新闻"

        risk_lines = []
        for a in analyses:
            if a.get("agent") == "RiskManager":
                for line in str(a.get("reasoning", "")).split("\n"):
                    cleaned = self._clean_bullet_line(line)
                    if cleaned and len(cleaned) > 4:
                        risk_lines.append(f"- {cleaned[:120]}")
        risk_block = "\n".join(risk_lines[:4]) if risk_lines else "- 暂无明显风险闸门触发"

        return (
            f"## 🎯 {symbol} 决策仪表盘\n\n"
            f"### {signal_icon} 结论\n"
            f"- **交易信号**: `{signal}`\n"
            f"- **置信度**: `{confidence}%`\n"
            f"- **建议仓位**: `{decision.get('position_size', '5-10%')}`\n\n"
            f"### 💰 交易计划\n"
            f"- **入场价**: `${decision.get('entry_price', 'N/A')}`\n"
            f"- **止损价**: `${decision.get('stop_loss', 'N/A')}`\n"
            f"- **目标价**: `${decision.get('target_price', 'N/A')}`\n\n"
            f"### 📰 关键新闻依据\n"
            f"{news_block}\n\n"
            f"### 🚨 风险提示\n"
            f"{risk_block}\n\n"
            f"> AI Stock Analyst"
        )
