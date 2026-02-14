# AI Stock Analyzer 🤖📈

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Ready-success)](https://github.com/features/actions)

> 🤖 AI-powered stock analysis system with RSS news aggregation, social media sentiment analysis, and multi-agent architecture

**Zero-cost deployment** · Scheduled execution · No server required

[简体中文](../README.md) | English

---

## ✨ Features

| Module | Feature | Description |
|--------|---------|-------------|
| 🤖 AI Analysis | Decision Dashboard | Core conclusion + precise entry/exit points + multi-dimensional scoring |
| 🧩 Multi-Agent | Role-based Reasoning | Technical + Fundamental + Bull + Bear + Risk Manager orchestration |
| 🛡️ Risk Gate | Hard Risk Override | Downgrades BUY under volatility/event/geopolitical risk |
| 📡 News | RSS Aggregation | Real-time news from Seeking Alpha, MarketWatch, CNBC, etc. |
| 🐦 Social | Sentiment Monitor | Twitter/X and Reddit discussion sentiment analysis |
| 🧠 LLM | Dual Model Support | Alibaba Bailian (primary) + Google Gemini (fallback) |
| 📱 Push | Multi-channel | Telegram, DingTalk, Feishu, WeChat Work |
| ⚡ Automation | GitHub Actions | Scheduled execution, zero-cost operation |

### Tech Stack

- **Python 3.11+** - Primary language
- **SQLite** - Embedded database (zero config)
- **FastAPI** - Web framework
- **Alibaba Bailian / Google Gemini** - Large Language Models
- **Structured + RSS sources** - Fed/SEC/CFTC/IMF + market feeds + Google News monitors

---

## 🚀 Quick Start

### Option 1: GitHub Actions (Recommended) - Zero-Cost Deployment

> **Deploy in 5 minutes, zero cost, no server needed!**

#### Step 1: Fork This Repository

1. Visit https://github.com/ZenKaiii
2. Find the `ai-stock-analyst` repository
3. Click the **Fork** button in the top right to copy to your account

#### Step 2: Configure Secrets (Critical)

Go to your forked repo → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

**Required Configuration:**

| Secret Name | Description | How to Get |
|-----------|------|----------|
| `BAILIAN_API_KEY` | Alibaba Cloud Bailian API Key | [Bailian Console](https://bailian.console.aliyun.com/) |
| `STOCK_LIST` | Stock symbols to analyze | e.g., `AAPL,TSLA,NVDA,MSFT` |

**Optional - Notification Channels (configure at least one):**

| Secret Name | Description | How to Get |
|-----------|------|----------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | Create bot with [@BotFather](https://t.me/botfather) |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | Get from [@userinfobot](https://t.me/userinfobot) |
| `DINGTALK_WEBHOOK_URL` | DingTalk Webhook | DingTalk Group → Settings → Smart Group Assistant → Add Robot → Custom |
| `FEISHU_WEBHOOK_URL` | Feishu Webhook | Feishu Group → Settings → Group Bots → Add Bot |
| `WECHAT_WORK_WEBHOOK_URL` | WeChat Work Webhook | WeChat Work Group → Group Settings → Add Group Bot |

**How to get Alibaba Bailian API Key:**

1. Visit https://bailian.console.aliyun.com/
2. Login with Alibaba Cloud account (register if needed)
3. Click "API Key Management" on the left
4. Click "Create New API Key"
5. Copy the key and add to GitHub Secrets

#### Step 3: Enable GitHub Actions

1. Click the **Actions** tab at the top of the repo
2. Click the green **"I understand my workflows, go ahead and enable them"** button
3. Workflows are now enabled

#### Step 4: Test Run Manually

1. Click the **Actions** tab
2. Select **"Daily Stock Analysis"** workflow on the left
3. Click the **"Run workflow"** dropdown on the right
4. Click the green **"Run workflow"** button
5. Wait for completion (about 2-5 minutes)

#### Step 5: View Results

1. Click the running workflow (blue link)
2. View the run logs to confirm successful completion
3. Check your notification channels (Telegram/DingTalk, etc.) for the push
4. You can also download analysis reports from Artifacts

**Done!** 🎉

The system will **automatically run at 5:00 AM Beijing Time, Tuesday-Saturday** (after US market closes Monday-Friday).

---

### Option 2: Local Run

```bash
# 1. Clone the repository
git clone https://github.com/ZenKaiii/ai-stock-analyst.git
cd ai-stock-analyst

# 2. Install dependencies
pip install -e .

# 3. Configure environment variables
cp .env.example .env
# Edit .env and add your API keys

# 4. Run analysis
python -m ai_stock_analyst.main --stocks AAPL,TSLA

# 5. Start web interface (optional)
python -m ai_stock_analyst.web.app
# Open http://localhost:8000
```

---

### Option 3: Docker Deployment

```bash
# 1. Start all services
docker-compose up -d

# 2. View logs
docker-compose logs -f

# 3. Stop services
docker-compose down
```

---

## 📋 Project Structure

```
ai-stock-analyst/
├── ai_stock_analyst/
│   ├── config/              # Configuration management
│   ├── database/            # SQLite database
│   ├── data/                # Stock data fetching + indicators
│   ├── rss/                 # RSS + structured event providers
│   ├── llm/                 # LLM routing (Bailian+Gemini)
│   ├── agents/              # Multi-agent analysis pipeline
│   ├── notification/        # Notification push (multi-platform)
│   └── main.py              # CLI entry point
├── .github/
│   └── workflows/
│       └── daily-analysis.yml   # GitHub Actions config
├── docs/
│   └── README_EN.md         # English documentation
├── docker-compose.yml
├── Dockerfile
├── .env.example             # Environment variables template
├── pyproject.toml
└── README.md                # This document (Chinese)
```

---

## 🔧 Detailed Configuration

## 📐 Spec Workflow

The repository includes a spec-driven execution scaffold:
- `.specify/memory/constitution.md`
- `specs/001-risk-aware-multi-agent-upgrade/spec.md`
- `specs/001-risk-aware-multi-agent-upgrade/plan.md`
- `specs/001-risk-aware-multi-agent-upgrade/tasks.md`

Recommended order:
1. Read constitution (hard constraints)
2. Confirm spec requirements
3. Execute by milestones in plan
4. Track completion in tasks checklist

## 🔄 Backtest Command

```bash
python scripts/backtest_strategy.py --symbols SPY,QQQ --period 2y --output-dir reports
```

Outputs:
- `reports/backtest_*.md`
- `reports/backtest_*.json`

## 🧾 IBKR Portfolio Sync (Optional)

You can sync holdings directly from IBKR TWS/Gateway:

```bash
pip install ib_async
# or: pip install ib_insync

stock-analyze --sync-ibkr-holdings
stock-analyze --sync-ibkr-holdings --portfolio
```

Environment variables:
- `IBKR_HOST` (default `127.0.0.1`)
- `IBKR_PORT` (default `7497`)
- `IBKR_CLIENT_ID` (default `21`)
- `IBKR_ACCOUNT` (optional account filter)

### Environment Variables (.env file)

```bash
# ===========================================
# Database Configuration (SQLite - Zero Config)
# ===========================================
DATABASE_URL=sqlite:///./data/stock_analyzer.db

# ===========================================
# LLM Configuration - Alibaba Bailian (Primary)
# Get at: https://bailian.console.aliyun.com/
# ===========================================
BAILIAN_API_KEY=sk-your-api-key-here
BAILIAN_REGION=singapore
BAILIAN_MODEL=qwen-plus

# ===========================================
# LLM Configuration - Google Gemini (Fallback)
# Get at: https://makersuite.google.com/app/apikey
# ===========================================
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro

# LLM routing strategy (auto failover)
LLM_PRIMARY=bailian
LLM_FALLBACK=gemini

# ===========================================
# Stock List (comma-separated)
# ===========================================
STOCK_LIST=AAPL,TSLA,NVDA,MSFT,GOOGL,AMZN,META

# ===========================================
# Notification Channels (configure at least one)
# ===========================================

# Telegram (recommended)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# DingTalk
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx

# Feishu
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx

# WeChat Work
WECHAT_WORK_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
```

### GitHub Actions Schedule Configuration

Default: Runs at 5:00 AM Beijing Time, Tuesday-Saturday (after US market closes)

To change the schedule, edit `.github/workflows/daily-analysis.yml`:

```yaml
on:
  schedule:
    # Format: minute hour day month weekday (UTC)
    # Beijing 5:00 AM = UTC 21:00 (previous day)
    - cron: '0 21 * * 1-5'  # Mon-Fri UTC 21:00
```

**Time Conversion:**
- UTC 21:00 = Beijing next day 5:00 AM
- UTC 13:00 = Beijing 9:00 PM
- UTC 00:00 = Beijing 8:00 AM

---

## 📱 Notification Examples

### Telegram Push

```
🟢 AAPL Analysis Result

Signal: BUY
Confidence: 78%
Suggested Entry: $185.50
Stop Loss: $176.23
Target: $204.05

Analysis Summary:
Technical indicators show bullish alignment, MACD golden cross, RSI in healthy range...

---
AI Stock Analyzer
```

### DingTalk/Feishu Push

Supports Markdown format, including:
- 📊 Analysis result summary
- 🎯 Buy/Sell signals
- 💰 Suggested prices (entry/stop/target)
- 📈 Technical analysis highlights
- 📰 Related news summary

---

## 💡 Why SQLite?

This project uses **SQLite** instead of PostgreSQL for the following advantages:

1. **Zero Configuration** - No database server installation or configuration needed
2. **GitHub Actions Friendly** - Runs seamlessly in CI/CD environments
3. **Zero Cost** - No external database service required
4. **Portable** - Single file database, easy to backup
5. **Sufficient** - More than enough performance for daily analysis tasks

**Data Persistence Strategy:**
- Fresh database created on each GitHub Actions run
- Analysis results pushed to notification channels (Telegram/DingTalk, etc.) as permanent records
- Report files uploaded as Artifacts (retained for 30 days)

---

## 🔍 Troubleshooting

### GitHub Actions Run Failed

1. **Check Secrets Configuration**
   - Verify `BAILIAN_API_KEY` is set correctly
   - Ensure no extra spaces

2. **View Run Logs**
   - Go to Actions → Click on the failed workflow
   - View specific error messages

3. **Test Locally**
   ```bash
   pip install -e .
   python -m src.main --stocks AAPL
   ```

### Not Receiving Notifications

1. **Check Notification Configuration Status**
   ```bash
   python -m src.main
   # View the notification channel configuration status in output
   ```

2. **Verify Secrets Are Set**
   - Configure at least one notification channel
   - Tokens/Keys should not have extra spaces

3. **Test Individual Channels**
   - Telegram: Send a message to the Bot first to confirm it can receive
   - DingTalk/Feishu: Check if the Webhook URL is correct

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit an Issue or Pull Request.

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

MIT License

---

**If this project helps you, please give it a ⭐ Star!**

For questions, please submit an [Issue](https://github.com/ZenKaiii/ai-stock-analyst/issues)
