# Spec 001: Risk-Aware Multi-Agent Upgrade

## Summary
将当前“轻量投票式”股票分析升级为“研究员分工 + 风控闸门 + 可回测评估”的可追溯决策系统。

## Problem Statement
当前系统可运行但存在以下限制：
1. 技术面特征不足（主要 MA5/MA20）。
2. 新闻/社媒以关键词情绪为主，结构化事件不足。
3. 最终决策缺少硬风险闸门。
4. 缺少策略级回测与置信度校准。

## Goals
1. 引入分工型 Agent（fundamental/bull/bear/risk/trader）并保持兼容现有 pipeline。
2. 建立风险闸门，能在高风险条件下强制降级信号。
3. 扩展指标特征并输出可追溯证据。
4. 增加最小可用回测流程与评估报告。

## Non-Goals
1. 本阶段不实现真实券商下单。
2. 本阶段不做高频/分钟级策略。
3. 本阶段不替换现有通知体系。

## User Stories
### Story 1 - As an analyst, I want transparent multi-agent reasoning
- Given 用户运行 `stock-analyze --stocks AAPL`
- When 系统完成分析
- Then 输出中包含各 Agent 结论、关键证据、冲突点与最终裁决理由

### Story 2 - As a risk-conscious investor, I want hard risk gating
- Given 事件风险或高波动触发
- When trader agent 产出 BUY
- Then 最终信号被 risk gate 降级为 HOLD，并附带触发条件

### Story 3 - As a maintainer, I want measurable strategy quality
- Given 新增策略模块
- When 执行回测脚本
- Then 生成包含收益、回撤、命中率的报告文件

## Functional Requirements
- FR-001: 系统 MUST 提供新增 Agent 接口与注册机制，最少包括 `FundamentalAnalyst`, `BullResearcher`, `BearResearcher`, `RiskManager`。
- FR-002: 系统 MUST 在最终决策前执行风险闸门，并记录触发项。
- FR-003: 系统 MUST 计算并暴露至少 RSI、MACD、ATR 三类指标。
- FR-004: 系统 MUST 对新闻源进行分层：结构化事件源优先，RSS 为补充。
- FR-005: 系统 MUST 产出可落盘的回测结果（JSON 或 Markdown）。
- FR-006: 当 LLM 或外部源不可用时，系统 MUST 返回可解释的 fallback 结果。

## Success Metrics
1. 输出透明度：单票分析中可见 Agent 级证据 >= 4 类。
2. 风控有效性：在高风险样本中，风险闸门触发率 > 90%。
3. 工程稳定性：外部数据源失败时 CLI 成功退出率 100%。
4. 评估覆盖度：新策略 PR 附带至少 1 份回测报告。

## Open Questions
1. 第一批结构化数据源优先接入哪一个（SEC / 财报日历 / 宏观日历）？
2. 回测频率先做日线还是支持周线对照？
