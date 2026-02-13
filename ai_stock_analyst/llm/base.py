"""
LLM基类定义
"""
from abc import ABC, abstractmethod
from typing import Dict, List


class BaseLLM(ABC):
    """LLM基类 - 定义通用接口"""
    
    @abstractmethod
    def chat(self, messages: List[Dict], **kwargs) -> Dict:
        """发送对话请求并返回结果"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查LLM是否可用"""
        pass
