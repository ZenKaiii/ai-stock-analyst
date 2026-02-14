# Tasks 003: Mobile Template, IBKR CPAPI, and Agent Upgrade

## Phase A - Mobile Template
- [x] T301 Refactor DingTalk mobile card layout in `ai_stock_analyst/notification/dingtalk.py`
- [x] T302 Expose richer agent sections in notifications in `ai_stock_analyst/notification/base.py`

## Phase B - IBKR CPAPI
- [x] T311 Add CPAPI holdings fetcher and mode switch in `ai_stock_analyst/broker/ibkr.py`
- [x] T312 Wire CPAPI envs in workflow and config docs
- [x] T313 Add beginner decision guide for web/mobile-only IBKR users in `README.md`

## Phase C - Agent Upgrade
- [x] T321 Add `MacroRegimeAgent` in `ai_stock_analyst/agents/macro_regime.py`
- [x] T322 Add `LiquidityQualityAgent` in `ai_stock_analyst/agents/liquidity_quality.py`
- [x] T323 Upgrade `FundamentalAnalyst` with earnings-stability scoring
- [x] T324 Add decision `score_100` in `ai_stock_analyst/agents/portfolio.py` and pipeline wiring
