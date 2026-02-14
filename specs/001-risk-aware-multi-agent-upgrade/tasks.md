# Tasks 001: Risk-Aware Multi-Agent Upgrade

## Phase 0 - Foundation
- [ ] T001 Create agent registry abstraction in `ai_stock_analyst/agents/analyzer.py`
- [ ] T002 Add feature-calculation module in `ai_stock_analyst/data/features.py`
- [ ] T003 Add unit-test scaffold in `tests/test_agent_registry.py`

## Phase 1 - New Agent Roles
- [ ] T101 Implement `FundamentalAnalyst` in `ai_stock_analyst/agents/fundamental.py`
- [ ] T102 Implement `BullResearcher` in `ai_stock_analyst/agents/bull_researcher.py`
- [ ] T103 Implement `BearResearcher` in `ai_stock_analyst/agents/bear_researcher.py`
- [ ] T104 Implement `RiskManager` in `ai_stock_analyst/agents/risk_manager.py`
- [ ] T105 Wire new agents in `ai_stock_analyst/agents/analyzer.py`
- [ ] T106 Add regression tests in `tests/test_multi_agent_pipeline.py`

## Phase 2 - Risk Gating and Indicators
- [ ] T201 Add RSI/MACD/ATR calculations in `ai_stock_analyst/data/features.py`
- [ ] T202 Integrate features into `ai_stock_analyst/data/fetcher.py`
- [ ] T203 Apply risk-gate before final signal in `ai_stock_analyst/agents/portfolio.py`
- [ ] T204 Add risk-gate tests in `tests/test_risk_gate.py`

## Phase 3 - Structured News + Backtest
- [ ] T301 Create provider interface in `ai_stock_analyst/rss/providers/base.py`
- [ ] T302 Add first structured event provider in `ai_stock_analyst/rss/providers/earnings_calendar.py`
- [ ] T303 Add provider orchestrator in `ai_stock_analyst/rss/feed.py`
- [ ] T304 Add backtest runner in `scripts/backtest_strategy.py`
- [ ] T305 Output backtest report to `reports/`
- [ ] T306 Add CI smoke test for backtest command in `.github/workflows/daily-analysis.yml`

## Phase 4 - Docs and Rollout
- [ ] T401 Update user guide in `README.md`
- [ ] T402 Add migration notes in `docs/README_EN.md`
- [ ] T403 Add release checklist in `specs/001-risk-aware-multi-agent-upgrade/plan.md`

## Parallelization Hints
- Can run in parallel: `T101/T102/T103`
- Can run in parallel: `T201/T301`
- Must be sequential: `T203` after `T104` and `T201`
