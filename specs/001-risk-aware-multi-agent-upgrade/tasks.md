# Tasks 001: Risk-Aware Multi-Agent Upgrade

## Phase 0 - Foundation
- [x] T001 Create agent registry abstraction in `ai_stock_analyst/agents/analyzer.py`
- [x] T002 Add feature-calculation module in `ai_stock_analyst/data/features.py`
- [x] T003 Add unit-test scaffold in `tests/test_agent_registry.py`

## Phase 1 - New Agent Roles
- [x] T101 Implement `FundamentalAnalyst` in `ai_stock_analyst/agents/fundamental.py`
- [x] T102 Implement `BullResearcher` in `ai_stock_analyst/agents/bull_researcher.py`
- [x] T103 Implement `BearResearcher` in `ai_stock_analyst/agents/bear_researcher.py`
- [x] T104 Implement `RiskManager` in `ai_stock_analyst/agents/risk_manager.py`
- [x] T105 Wire new agents in `ai_stock_analyst/agents/analyzer.py`
- [x] T106 Add regression tests in `tests/test_multi_agent_pipeline.py`

## Phase 2 - Risk Gating and Indicators
- [x] T201 Add RSI/MACD/ATR calculations in `ai_stock_analyst/data/features.py`
- [x] T202 Integrate features into `ai_stock_analyst/data/fetcher.py`
- [x] T203 Apply risk-gate before final signal in `ai_stock_analyst/agents/portfolio.py`
- [x] T204 Add risk-gate tests in `tests/test_risk_gate.py`

## Phase 3 - Structured News + Backtest
- [x] T301 Create provider interface in `ai_stock_analyst/rss/providers/base.py`
- [x] T302 Add first structured event provider in `ai_stock_analyst/rss/providers/earnings_calendar.py`
- [x] T303 Add provider orchestrator in `ai_stock_analyst/rss/feed.py`
- [x] T304 Add backtest runner in `scripts/backtest_strategy.py`
- [x] T305 Output backtest report to `reports/`
- [x] T306 Add CI smoke test for backtest command in `.github/workflows/daily-analysis.yml`

## Phase 4 - Docs and Rollout
- [x] T401 Update user guide in `README.md`
- [x] T402 Add migration notes in `docs/README_EN.md`
- [x] T403 Add release checklist in `specs/001-risk-aware-multi-agent-upgrade/plan.md`

## Parallelization Hints
- Can run in parallel: `T101/T102/T103`
- Can run in parallel: `T201/T301`
- Must be sequential: `T203` after `T104` and `T201`
