"""
Google Gemini LLM实现 - 使用新版 google-genai SDK
"""
import os
import logging
from typing import Dict, List
from .base import BaseLLM

logger = logging.getLogger(__name__)


class GeminiLLM(BaseLLM):
    """Google Gemini大模型客户端 - 新版 SDK"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.available = bool(self.api_key)
        self._client = None

        if self.available:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info(f"Gemini initialized: {self.model}")
            except Exception as e:
                logger.error(f"Failed to init Gemini: {e}")
                self.available = False

    def is_available(self) -> bool:
        return self.available and self._client is not None

    def chat(self, messages: List[Dict], temperature: float = 0.3,
             max_tokens: int = 2000) -> Dict:
        if not self.is_available():
            raise Exception("Gemini not available")

        try:
            contents = self._convert_messages(messages)

            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )

            return {
                "content": response.text,
                "model": self.model,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    def _convert_messages(self, messages: List[Dict]) -> str:
        """将消息列表转换为字符串格式"""
        parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                parts.append(f"System: {content}\n")
            elif role == "user":
                parts.append(f"User: {content}\n")
            elif role == "assistant":
                parts.append(f"Assistant: {content}\n")
        return "\n".join(parts)
