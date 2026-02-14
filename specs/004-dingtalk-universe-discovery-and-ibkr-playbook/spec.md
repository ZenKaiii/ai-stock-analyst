# Spec 004: DingTalk Rendering Fix, Universe Discovery, and IBKR Playbook

## Summary
本迭代处理三个痛点：
1) 修复钉钉 markdown 渲染中的粗体/星号异常，优化移动端展示一致性；
2) 将热门股票发现从“少量新闻候选”升级为“全市场候选池 -> 预筛 -> 深度评分 -> Top1+20备选”；
3) 基于官方文档与 thetagang 实践，给出可执行的 IBKR 接入与交易自动化路线。

## Problem Statement
- 钉钉端对 markdown 子集支持有限，当前粗体与列表混用导致格式噪音。
- 当前推荐仅 Top5，无法体现“全市场扫描”和层级筛选过程。
- 用户仅有 IBKR web/mobile，缺少可直接执行的接入方案与落地步骤。

## Goals
- G1: 钉钉输出稳定、无残留星号、无重复标题。
- G2: 推荐结果输出 Top1 + 20备选，并包含“扫描/初筛/评分”统计。
- G3: 文档明确 web/mobile-only 用户如何使用 CPAPI，及交易自动化演进路径。

## Functional Requirements
- FR-401: DingTalk formatter MUST 降级不稳定 markdown（粗体/行内代码）并保留结构化层级。
- FR-402: Discover MUST 支持全市场候选池加载、预筛和评分，输出 Top1 + Top20。
- FR-403: Discover 输出 MUST 包含统计：扫描数、预筛数、评分数、最终推荐数。
- FR-404: README MUST 增加 thetagang 对照分析与 IBKR 接入路线图。
- FR-405: CLI MUST 支持 discovery universe/prefilter/final 参数配置。

## Success Metrics
- M1: 钉钉消息不出现残留 `*` 或重复标题。
- M2: 默认推荐输出 >= 21 条（Top1 + 20备选）。
- M3: 用户可按文档完成 CPAPI 模式自检命令并拿到明确结果。
