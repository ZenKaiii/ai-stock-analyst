# Spec 003: Mobile Template, IBKR CPAPI, and Agent Upgrade

## Summary
在保持现有稳定性的前提下，进一步提升三项能力：
1) 钉钉移动端消息模板可读性（强分段、强层级、留白）；
2) 增加 IBKR Client Portal API (CPAPI) 路径，支持仅网页/移动端用户的持仓拉取；
3) 吸收“8-Agent”思路，新增宏观、流动性与财报稳定性分析维度。

## Problem Statement
1. 钉钉消息在手机端仍存在“信息密度高、视觉节奏弱”的问题。
2. 用户没有 TWS/Gateway 时，现有 Socket API 路径不可用。
3. 当前多 Agent 尚缺“宏观 regime + 流动性质量 + 财报稳定性”三类结构化判断。

## Goals
1. 形成统一的手机端决策卡模板，强化可扫读体验。
2. 通过 `IBKR_API_MODE=cpapi` 提供可执行的 CPAPI 持仓同步流程。
3. 将宏观、流动性、财报稳定性信号纳入决策与通知呈现。

## Functional Requirements
- FR-301: 钉钉分析消息 MUST 使用卡片化结构（结论、计划、宏观、流动性、财报、新闻、风险、行动）。
- FR-302: 系统 MUST 支持 `IBKR_API_MODE=cpapi|socket|auto` 并在失败时给出明确引导。
- FR-303: CPAPI 模式 MUST 支持 `/portfolio/accounts` + `/portfolio/{accountId}/positions` 读取持仓。
- FR-304: Agent 流水线 MUST 新增宏观与流动性角色，并增强财报稳定性评估。
- FR-305: README MUST 提供“仅网页/移动端用户”可执行路径（含限制与自动化边界）。

## Success Metrics
1. 单条钉钉消息段落结构 >= 8 个小节，且每节不超过 4 条要点。
2. IBKR 同步错误日志可区分：未认证、网关不可达、账户未识别三类。
3. 决策结果包含 `score_100`，用于排序与对比。
