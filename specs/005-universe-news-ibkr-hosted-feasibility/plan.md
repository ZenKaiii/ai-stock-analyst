# Plan 005: Exchange + News + IBKR Feasibility

## Architecture
- Data layer:
  - `ai_stock_analyst/data/universe.py` 增加 `load_us_equity_universe_with_stats`，输出 symbols + exchange_breakdown。
- Recommendation layer:
  - `ai_stock_analyst/agents/recommendation.py` 接入交易所统计与 source quality；
  - fallback 改为 `top_k` 驱动，默认 21（Top1+20）。
- Notification layer:
  - `ai_stock_analyst/notification/dingtalk.py` 增强 markdown 降级，彻底清理残留星号。
- News ingestion:
  - `ai_stock_analyst/rss/feed.py` 增补 NYT/Investing/News Minimalist/CISA。
- Delivery / CI:
  - `.github/workflows/daily-analysis.yml` 增加 cpapi hosted-runner 前置校验。

## Testing Strategy (TDD)
- 先写失败测试：
  - `tests/test_dingtalk_markdown.py`：残留星号清理。
  - `tests/test_universe_coverage.py`：NYSE/AMEX 覆盖与 ETF 过滤。
  - `tests/test_recommendation_fallback.py`：fallback 支持 Top21 + 文本不含强调残留。
  - `tests/test_discovery_scoring.py`：source quality 得分偏好。
- 再实现最小改动使测试通过，最后跑全量测试。

## Rollout
- 默认 discover universe 改为 `0`（全量模式）；workflow 默认变量保持可控（3200）避免 CI 超时。
- 文档明确：IBKR web/mobile-only 用户在 github-hosted runner 下不可直接连本地 cp gateway。
