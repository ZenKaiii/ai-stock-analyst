# Plan 001: Risk-Aware Multi-Agent Upgrade

## Context
- Repo: `ai-stock-analyst`
- Existing flow: `main.py` -> `analyzer.py` -> agents -> notifications
- Constraints: 保持 GitHub Actions 现有入口参数兼容

## Technical Approach
1. 在 `ai_stock_analyst/agents/` 增加新角色 Agent，沿用 `BaseAgent` 协议。
2. 在 `ai_stock_analyst/data/` 增加特征计算层，统一输出技术指标与风险特征。
3. 在 `PortfolioManager` 前插入 `RiskManager` 决策闸门。
4. 在 `scripts/` 新增回测入口，读取历史数据生成评估报告。

## Milestones

### M1 - Agent 架构增强
- 新增 `fundamental.py`, `bull_researcher.py`, `bear_researcher.py`, `risk_manager.py`
- 更新 `analyzer.py` 注入新 Agent 与执行顺序
- 验收: CLI 输出包含新增 Agent 结果

### M2 - 特征与风险闸门
- 新增技术指标计算模块（RSI/MACD/ATR）
- 风险闸门支持事件风险、波动率、数据质量三项输入
- 验收: 触发风险时 final signal 可自动降级

### M3 - 数据源与评估
- 新增结构化事件数据抽象层（provider interface）
- 新增最小回测脚本与报告输出
- 验收: 生成 `reports/backtest_*.md`

## Risks and Mitigations
1. 数据源不稳定
- Mitigation: provider failover + 缓存 + fallback
2. LLM 输出不稳定
- Mitigation: schema parser + rule fallback
3. 决策链过长导致延迟
- Mitigation: 限制每个 Agent token、并发抓取数据

## Compatibility
- 保留现有 CLI 参数：`--stocks --type --discover --portfolio`
- 保留现有通知通道逻辑
- 默认行为不破坏现有 GitHub Action workflow

## Definition of Done
1. Spec 对应代码合并并可在本地运行。
2. 新增/更新测试覆盖关键决策路径。
3. README 更新包含新流程与运行方式。
