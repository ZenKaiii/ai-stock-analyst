"""
阿里云百炼LLM实现
"""
import os
import logging
from typing import Dict, List
from .base import BaseLLM

logger = logging.getLogger(__name__)


class BailianLLM(BaseLLM):
    """阿里云百炼大模型客户端"""
    
    # 区域端点配置
    ENDPOINTS = {
        "singapore": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "us": "https://dashscope-us.aliyuncs.com/compatible-mode/v1",
        "beijing": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    }
    
    def __init__(self):
        self.api_key = os.getenv("BAILIAN_API_KEY")
        self.region = os.getenv("BAILIAN_REGION", "singapore")
        self.model = os.getenv("BAILIAN_MODEL", "deepseek-v3")
        
        self.base_url = self.ENDPOINTS.get(self.region, self.ENDPOINTS["singapore"])
        self.available = bool(self.api_key)
        self._client = None
        
        if self.available:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                logger.info(f"Bailian initialized: {self.model} @ {self.region}")
            except Exception as e:
                logger.error(f"Failed to init Bailian: {e}")
                self.available = False
    
    def is_available(self) -> bool:
        return self.available and self._client is not None
    
    def chat(self, messages: List[Dict], temperature: float = 0.3, 
             max_tokens: int = 2000) -> Dict:
        if not self.is_available():
            raise Exception("Bailian not available")
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            logger.error(f"Bailian API error: {e}")
            raise
