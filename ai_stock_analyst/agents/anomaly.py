"""
异常检测Agent - 检测市场异常行为（异动、突发交易量等）
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from ai_stock_analyst.agents.base import BaseAgent, AnalysisResult

logger = logging.getLogger(__name__)


class AnomalyAgent(BaseAgent):
    """
    异常检测Agent
    功能：
    1. 交易量异常检测 (Volume Spike)
    2. 价格剧烈波动检测 (Price Volatility)
    3. 跳空缺口检测 (Gap Up/Down)
    """
    
    def __init__(self):
        super().__init__("AnomalyAgent")
        self.z_threshold = 3.0  # Z-score阈值，超过3倍标准差视为异常
    
    def analyze(self, data: Dict) -> AnalysisResult:
        """
        执行异常检测
        """
        price_data = data.get("price_data", {})
        history = price_data.get("history")
        
        # 如果没有历史数据（DataFrame），无法进行统计分析
        if history is None or history.empty or len(history) < 20:
            return AnalysisResult(
                agent_name=self.name,
                signal="HOLD",
                confidence=0.0,
                reasoning="历史数据不足，无法进行异常检测",
                indicators={},
                risks=[]
            )
        
        anomalies = []
        indicators = {}
        risk_score = 0
        
        # 1. 交易量异常检测
        try:
            current_volume = history["Volume"].iloc[-1]
            volume_mean = history["Volume"].mean()
            volume_std = history["Volume"].std()
            
            if volume_std > 0:
                volume_z_score = (current_volume - volume_mean) / volume_std
                indicators["volume_z_score"] = round(volume_z_score, 2)
                
                if volume_z_score > self.z_threshold:
                    msg = f"交易量激增 (Z-score: {volume_z_score:.2f})，可能是重大消息驱动"
                    anomalies.append(f"🚨 {msg}")
                    risk_score += 1
                elif volume_z_score < -2.0:
                    anomalies.append("📉 交易量极度萎缩，市场关注度下降")
        except Exception as e:
            logger.warning(f"Volume check failed: {e}")

        # 2. 价格波动检测 (Daily Returns Z-score)
        try:
            # 计算日收益率
            returns = history["Close"].pct_change().dropna()
            if not returns.empty:
                current_return = returns.iloc[-1]
                return_mean = returns.mean()
                return_std = returns.std()
                
                if return_std > 0:
                    price_z_score = (current_return - return_mean) / return_std
                    indicators["price_z_score"] = round(price_z_score, 2)
                    
                    if abs(price_z_score) > self.z_threshold:
                        direction = "暴涨" if price_z_score > 0 else "暴跌"
                        msg = f"价格异常{direction} (Z-score: {price_z_score:.2f})"
                        anomalies.append(f"⚡ {msg}")
                        risk_score += 2
        except Exception as e:
            logger.warning(f"Volatility check failed: {e}")

        # 3. 跳空缺口检测 (Gap Detection)
        try:
            if len(history) >= 2:
                prev_close = history["Close"].iloc[-2]
                curr_open = history["Open"].iloc[-1]
                
                gap_percent = (curr_open - prev_close) / prev_close * 100
                indicators["gap_percent"] = round(gap_percent, 2)
                
                if gap_percent > 2.0:
                    anomalies.append(f"🚀 跳空高开 +{gap_percent:.2f}%")
                elif gap_percent < -2.0:
                    anomalies.append(f"🕳️ 跳空低开 {gap_percent:.2f}%")
                    risk_score += 1
        except Exception as e:
            logger.warning(f"Gap check failed: {e}")

        # 构建结论
        if not anomalies:
            signal = "HOLD"
            confidence = 0.5
            reasoning = "未检测到明显的市场异动，走势相对平稳。"
        else:
            # 异动通常意味着高风险或机会
            reasoning = "**检测到以下市场异动：**\n" + "\n".join(anomalies)
            
            # 简单的信号逻辑：放量上涨视为机会，暴跌视为风险
            last_return = history["Close"].pct_change().iloc[-1]
            if risk_score > 0:
                if last_return > 0 and "交易量激增" in str(anomalies):
                    signal = "BUY"
                    confidence = 0.7
                    reasoning += "\n\n**分析**：放量上涨，动能强劲。"
                elif last_return < -0.03: # 跌幅超过3%
                    signal = "SELL" # 建议避险
                    confidence = 0.6
                    reasoning += "\n\n**警告**：跌幅过大，建议注意风险。"
                else:
                    signal = "HOLD"
                    confidence = 0.5
            else:
                signal = "HOLD"
                confidence = 0.5

        return AnalysisResult(
            agent_name=self.name,
            signal=signal,
            confidence=confidence,
            reasoning=reasoning,
            indicators=indicators,
            risks=anomalies if risk_score > 0 else []
        )
