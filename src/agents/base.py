"""
Agent基类
"""
from abc import ABC, abstractmethod
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    agent_name: str
    signal: str
    confidence: float
    reasoning: str
    indicators: Dict
    risks: List[str]


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def analyze(self, data: Dict) -> AnalysisResult:
        pass
    
    def call_llm(self, prompt: str, system: str = "") -> str:
        """调用LLM"""
        from src.llm import get_llm_router
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        result = get_llm_router().chat(messages)
        return result["content"]
