# Plan 003: Mobile Template, IBKR CPAPI, and Agent Upgrade

## Milestone A - Mobile Template
- 重构钉钉移动端模板为“卡片式分组”
- 合并重复标题/重复 bullet，控制单段长度
- 引入评分与可执行建议区块

## Milestone B - IBKR CPAPI Support
- 在 `broker/ibkr.py` 新增 CPAPI fetcher
- 增加 `IBKR_API_MODE` 与 CPAPI 相关环境变量
- 在 workflow 与文档中补齐 CPAPI 场景说明

## Milestone C - Agent Capability Upgrade
- 新增 `MacroRegimeAgent`
- 新增 `LiquidityQualityAgent`
- 升级 `FundamentalAnalyst` 的财报稳定性打分
- 在组合决策层补充 `score_100`

## Definition of Done
- 语法检查通过
- README 与 README_EN 更新
- specs/003 任务全部勾选
