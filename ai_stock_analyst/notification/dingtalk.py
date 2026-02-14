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
        text = self._strip_duplicate_heading(title, text)
        text = text.replace("---", "\n\n---\n\n")
        text = re.sub(r"^[ \t]*•\s*", "- ", text, flags=re.MULTILINE)
        text = re.sub(r"^[ \t]*[-*][ \t]*[•·*-][ \t]*", "- ", text, flags=re.MULTILINE)
        text = re.sub(r"^[ \t]*[•·][ \t]*[•·][ \t]*", "- ", text, flags=re.MULTILINE)
        text = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", text)
        # 避免过深标题在钉钉端显示不稳定
        text = re.sub(r"^####\s+", "### ", text, flags=re.MULTILINE)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return f"## {title}\n\n{text}"

    def _strip_duplicate_heading(self, title: str, content: str) -> str:
        lines = content.splitlines()
        if not lines:
            return content
        title_norm = self._normalize_heading_for_compare(title)
        idx = 0
        while idx < len(lines) and not lines[idx].strip():
            idx += 1
        if idx < len(lines):
            first = lines[idx].strip()
            heading = re.sub(r"^\s*#+\s*", "", first).strip()
            if heading and title_norm and self._normalize_heading_for_compare(heading) == title_norm:
                lines = lines[:idx] + lines[idx + 1 :]
        return "\n".join(lines).strip()

    def _normalize_heading_for_compare(self, text: str) -> str:
        text = re.sub(r"[*_`#>\-]", "", text)
        text = re.sub(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", "", text)
        text = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "", text)
        return text.lower().strip()

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
            summary = self._clean_bullet_line(item.get("summary", ""))[:120]
            link = item.get("link", "")
            source = item.get("source", "Unknown")
            if title:
                brief = summary if summary else "暂无摘要，建议查看原文。"
                impact = self._infer_news_impact(title, summary)
                news_lines.append(f"{idx}. **[{source}]** {title}")
                news_lines.append(f"   - 概要: {brief}")
                news_lines.append(f"   - 解读: {impact}")
                if link:
                    news_lines.append(f"   - [查看原文]({link})")
        news_block = "\n".join(news_lines) if news_lines else "1. 暂无重点新闻"

        risk_lines = []
        for a in analyses:
            if a.get("agent") == "RiskManager":
                for line in str(a.get("reasoning", "")).split("\n"):
                    cleaned = self._clean_bullet_line(line)
                    if cleaned and len(cleaned) > 4:
                        risk_lines.append(f"- {cleaned[:120]}")
        risk_block = "\n".join(risk_lines[:4]) if risk_lines else "- 暂无明显风险闸门触发"

        technical_lines = self._extract_agent_lines(analyses, "TechnicalAnalyst", limit=4)
        tech_block = "\n".join(f"- {line}" for line in technical_lines) if technical_lines else "- 技术面信息不足，建议观察量价变化。"
        rationale = self._clean_bullet_line(str(decision.get("rationale", "")))[:120] or "建议结合仓位与风险偏好执行。"
        action_for_new = "可小仓位分批试错，严格止损。" if signal == "BUY" else "优先观望，等待趋势确认。" if signal == "HOLD" else "不建议新开仓，先控制回撤。"
        action_for_holding = "已有仓位可继续持有，跌破止损位及时减仓。" if signal != "SELL" else "已有仓位建议分批减仓或止损。"

        return (
            f"## 🎯 {symbol} 决策仪表盘\n\n"
            f"### {signal_icon} 结论\n"
            f"- **交易信号**: `{signal}`\n"
            f"- **置信度**: `{confidence}%`\n"
            f"- **建议仓位**: `{decision.get('position_size', '5-10%')}`\n\n"
            f"> {rationale}\n\n"
            f"### 💰 交易计划\n"
            f"- **入场价**: `${decision.get('entry_price', 'N/A')}`\n"
            f"- **止损价**: `${decision.get('stop_loss', 'N/A')}`\n"
            f"- **目标价**: `${decision.get('target_price', 'N/A')}`\n\n"
            f"### 📊 技术面要点\n"
            f"{tech_block}\n\n"
            f"### 📰 关键新闻依据\n"
            f"{news_block}\n\n"
            f"### 🚨 风险提示\n"
            f"{risk_block}\n\n"
            f"### 📚 小白指标速读\n"
            f"- **RSI**: >70 常见为短期偏热，<30 常见为短期偏弱。\n"
            f"- **MACD**: 柱线转正通常代表动能改善，转负代表动能走弱。\n"
            f"- **ATR%**: 越高代表波动越大，仓位应越小。\n\n"
            f"### ✅ 行动建议（小白版）\n"
            f"- **空仓用户**: {action_for_new}\n"
            f"- **持仓用户**: {action_for_holding}\n\n"
            f"> AI Stock Analyst"
        )

    def _extract_agent_lines(self, analyses, agent_name: str, limit: int = 3):
        for item in analyses:
            if item.get("agent") != agent_name:
                continue
            lines = []
            for raw in str(item.get("reasoning", "")).splitlines():
                cleaned = self._clean_bullet_line(raw)
                if cleaned and len(cleaned) >= 8:
                    lines.append(cleaned[:120])
                if len(lines) >= limit:
                    break
            return lines
        return []

    def _infer_news_impact(self, title: str, summary: str) -> str:
        text = f"{title} {summary}".lower()
        if any(k in text for k in ["earnings", "beat", "guidance", "财报", "超预期", "指引"]):
            return "属于业绩类事件，若利润或指引超预期通常利好估值。"
        if any(k in text for k in ["trump", "tariff", "sanction", "关税", "制裁", "政策"]):
            return "属于政策/地缘政治事件，可能放大板块波动，需降低仓位。"
        if any(k in text for k in ["partnership", "contract", "订单", "签约", "合作"]):
            return "属于订单或合作催化，可能改善收入预期。"
        return "信息偏中性，建议结合后续价格与成交量确认。"
