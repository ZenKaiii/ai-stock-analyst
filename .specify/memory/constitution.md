# AI Stock Analyst Constitution

## Purpose
本宪章定义本项目在“多 Agent 股票分析”演进中的硬约束，用于约束后续所有 spec / plan / tasks 的设计与交付。

## Core Principles

### 1. Signal Traceability First
每个交易信号必须可追溯到输入数据、特征计算与决策链路。
- MUST: 任何 BUY/SELL/HOLD 输出均包含来源（价格、新闻、社媒、风险）与时间戳。
- MUST: 记录 Agent 级别中间结论，禁止仅输出黑盒结论。

### 2. Risk Is a Hard Gate
风险控制优先于收益追求。
- MUST: 在最终决策阶段引入风险闸门（波动、事件、集中度、数据质量）。
- MUST: 当风险闸门触发时，最终信号必须降级（例如 BUY -> HOLD）。

### 3. Backtest Before Promotion
策略必须先经过离线验证再进入默认执行路径。
- MUST: 新增核心策略时提供最小回测或回放评估结果。
- MUST: 在文档中定义评估指标（命中率、回撤、风险收益比）。

### 4. Deterministic Fallback
LLM 不可用时系统仍需稳定运行。
- MUST: 关键分析模块提供规则化 fallback，且行为可测试。
- MUST: 所有外部数据源失败时输出降级报告而非中断。

### 5. Incremental Delivery
所有功能采用小步可回滚迭代。
- MUST: 每个 spec 至少可在 1 个里程碑内交付可用价值。
- MUST: 优先修改现有模块，避免大规模重写。

## Governance
- 宪章优先级高于普通设计偏好。
- 若某项实现违反宪章，必须在 spec 中显式记录豁免理由与回收计划。
- 宪章修订需在 PR 中单独列出“变更原因/影响/迁移策略”。
