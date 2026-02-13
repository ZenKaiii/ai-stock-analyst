"""
LLM路由 - 智能切换多个LLM提供商
"""
import os
import logging
from typing import Dict, List
from .base import BaseLLM
from .bailian import BailianLLM
from .gemini import GeminiLLM

logger = logging.getLogger(__name__)


class LLMRouter:
    """LLM路由器 - 自动failover"""
    
    def __init__(self):
        self.providers = {
            "bailian": BailianLLM(),
            "gemini": GeminiLLM(),
        }
        self.primary = os.getenv("LLM_PRIMARY", "bailian")
        self.fallback = os.getenv("LLM_FALLBACK", "gemini")
    
    def chat(self, messages: List[Dict], **kwargs) -> Dict:
        """发送消息，自动failover"""
        primary_llm = self.providers.get(self.primary)
        if primary_llm and primary_llm.is_available():
            try:
                logger.info(f"Using primary LLM: {self.primary}")
                result = primary_llm.chat(messages, **kwargs)
                result["provider"] = self.primary
                return result
            except Exception as e:
                logger.warning(f"Primary LLM {self.primary} failed: {e}")
        
        fallback_llm = self.providers.get(self.fallback)
        if fallback_llm and fallback_llm.is_available():
            try:
                logger.info(f"Falling back to: {self.fallback}")
                result = fallback_llm.chat(messages, **kwargs)
                result["provider"] = self.fallback
                return result
            except Exception as e:
                logger.error(f"Fallback LLM {self.fallback} failed: {e}")
                raise
        
        raise Exception("No LLM provider available")


# 全局实例
_llm_router = None


def get_llm_router() -> LLMRouter:
    """获取LLM路由器实例（单例）"""
    global _llm_router
    if _llm_router is None:
        _llm_router = LLMRouter()
    return _llm_router
