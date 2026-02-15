# Spec 005: Exchange Completeness, News Quality Upgrade, and IBKR GitHub Actions Feasibility

## Summary
本迭代聚焦三个目标：
1. 明确并增强美股候选池覆盖（NASDAQ + NYSE + NYSE American + Arca 等），输出交易所分布统计；
2. 修复钉钉 markdown 星号残留与强调渲染异常，保证移动端展示稳定；
3. 明确 IBKR 在 GitHub Actions 场景（仅 web/mobile 用户）可行边界，并给出可执行路径。

## Problem Statement
- 用户担心候选池仅覆盖 NASDAQ，遗漏 NYSE/AMEX。
- 钉钉中出现 `结论*`、`交易信号*` 等残留符号，影响阅读。
- 回退路径仍偏 Top5，未体现“全市场扫描 -> 初筛 -> 评分 -> Top1+20”。
- 仅有 IBKR web/mobile 时，GitHub hosted runner 的接入可行性不清晰。

## Goals
- G1: 候选池支持交易所覆盖说明与统计输出。
- G2: 钉钉消息不出现残留 `*` 与行内代码符号。
- G3: 回退路径与主路径统一到 Top1+20 推荐规模。
- G4: 给出 IBKR Actions 场景的“能/不能”结论与前置校验。

## Functional Requirements
- FR-501: Universe loader MUST 支持 `max_symbols<=0` 全量模式，并返回交易所分布统计。
- FR-502: Discover summary MUST 展示交易所覆盖统计。
- FR-503: DingTalk formatter MUST 清理未成对强调符号，并降级不稳定 markdown 语法。
- FR-504: Recommendation fallback MUST 支持 `top_k`（默认 21）而非固定 Top5。
- FR-505: RSS sources MUST 增加可用高质量补充源（NYT Business/Economy、Investing、News Minimalist、CISA）。
- FR-506: IBKR workflow MUST 在 `cpapi + github-hosted + localhost` 场景下快速失败并提示使用 self-hosted runner。

## Success Metrics
- M1: `tests/test_dingtalk_markdown.py` 中“残留星号”用例通过。
- M2: 回退路径推荐数量单测可达到 21。
- M3: 全量测试通过，且 discover 结果包含 `exchange_breakdown`。
- M4: `specify check` 通过，spec 目录新增本迭代文档。
