# Spec 002: Beginner-Friendly Dashboard and IBKR Onboarding

## Summary
面向金融小白，重构分析推送与热门荐股展示，使内容“可读、可懂、可执行”；同时补齐 IBKR API 接入说明与可运行流程。

## Problem Statement
1. 钉钉推送虽有 markdown，但信息层次与解释不足，阅读负担大。
2. 热门股票发现中英文混杂、新闻解释不足，小白无法判断“为什么推荐”。
3. IBKR 使用方式不透明，Action 与本地连接边界不清晰，易配置失败。

## Goals
1. 钉钉决策仪表盘提供完整结构：结论、价格计划、新闻依据、风险、指标解释、行动建议。
2. 热门股票发现默认中文输出，包含公司/行业/业务简介、新闻事件概述、推荐原因解释。
3. 给出 IBKR Socket API 与 Client Portal API 的鉴权与调用路径对比，并在项目中提供可执行入口与文档。

## Functional Requirements
- FR-001: 分析模式推送 MUST 对金融小白解释关键指标含义（如 RSI/MACD/ATR/止损）。
- FR-002: 热门股输出 MUST 包含公司名称、行业分类、新闻概述与“为何利好/利空”的中文解释。
- FR-003: 热门股候选 MUST 进行噪声过滤，避免无关或证据不足标的优先展示。
- FR-004: IBKR 文档 MUST 明确 `HOST/PORT/CLIENT_ID/ACCOUNT` 含义与确认步骤。
- FR-005: Workflow 中 IBKR 模式 MUST 在同步失败时快速失败并给出可读报错。

## Success Metrics
1. 钉钉消息中每个股票的结构化小节 >= 5。
2. 热门股每只至少 1 条中文新闻解读。
3. IBKR 常见配置错误可在日志中被清晰识别（空端口、不可达主机、未登录网关）。
