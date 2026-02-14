# AI股票分析系统 🤖📈

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Ready-success)](https://github.com/features/actions)

> 🤖 基于AI大模型的美股智能分析系统，每日自动分析并推送「决策仪表盘」到Telegram/钉钉/飞书/企业微信

**零成本部署** · 定时运行 · 无需服务器

简体中文 | [English](docs/README_EN.md)

---

## ✨ 功能特性

| 模块 | 功能 | 说明 |
|------|------|------|
| 🤖 AI分析 | 决策仪表盘 | 核心结论 + 精确买卖点位 + 多维度评分 |
| 🧩 多Agent协作 | 研究员分工 | Technical + Fundamental + Bull + Bear + RiskManager 协同决策 |
| 🛡️ 风控 | Risk Gate | 高波动/事件窗口/数据质量异常时自动降级 BUY 信号 |
| 🌍 地缘政治 | 宏观事件风控 | 纳入地缘政治与Trump政策动态对美股冲击评估 |
| 📡 新闻 | RSS+结构化事件 | SeekingAlpha/WSJ/CNBC + Fed/SEC/CFTC/IMF + Geopolitical监控 |
| 🐦 社媒 | 情绪监控 | Twitter/X和Reddit讨论情绪分析 |
| 🧠 LLM | 双模型支持 | 阿里云百炼 DeepSeek(主要) + Google Gemini(备用) |
| 📱 推送 | 多渠道通知 | Telegram、钉钉、飞书、企业微信 |
| ⚡ 自动化 | GitHub Actions | 定时执行，零成本运行 |

### 技术栈

- **Python 3.11+** - 主要编程语言
- **SQLite** - 嵌入式数据库（零配置）
- **FastAPI** - Web框架
- **阿里云百炼 / Google Gemini** - 大语言模型
- **RSS + Structured Providers** - RSS聚合与结构化事件源

---

## 🚀 快速开始

### 方式一：GitHub Actions（推荐）- 零成本部署

> **5分钟完成部署，零成本，无需服务器！**

#### 第一步：Fork本仓库

1. 访问 https://github.com/ZenKaiii
2. 找到 `ai-stock-analyst` 仓库
3. 点击右上角 **Fork** 按钮，将仓库复制到你的账号下

#### 第二步：配置Secrets（关键步骤）

进入你Fork的仓库 → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

**必需配置项：**

| Secret名称 | 说明 | 获取方式 |
|-----------|------|----------|
| `BAILIAN_API_KEY` | 阿里云百炼 API Key | [阿里云百炼控制台](https://bailian.console.aliyun.com/) |
| `STOCK_LIST` | 要分析的股票代码 | 如：`AAPL,TSLA,NVDA,MSFT` |

**可选 - LLM 备用配置：**

| Secret名称 | 说明 | 获取方式 |
|-----------|------|----------|
| `GEMINI_API_KEY` | Google Gemini API Key（备用） | [Google AI Studio](https://makersuite.google.com/app/apikey) |

**可选 - 通知渠道（至少配置一个）：**

| Secret名称 | 说明 | 获取方式 |
|-----------|------|----------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | [@BotFather](https://t.me/botfather) 创建机器人 |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | [@userinfobot](https://t.me/userinfobot) 获取 |
| `DINGTALK_WEBHOOK_URL` | 钉钉Webhook | 钉钉群 → 群设置 → 智能群助手 → 添加机器人 → 自定义 |
| `FEISHU_WEBHOOK_URL` | 飞书Webhook | 飞书群 → 设置 → 群机器人 → 添加机器人 |
| `WECHAT_WORK_WEBHOOK_URL` | 企业微信Webhook | 企业微信群 → 群设置 → 添加群机器人 |

**如何获取阿里云百炼 API Key（必需）：**

1. 访问 https://bailian.console.aliyun.com/
2. 使用阿里云账号登录
3. 点击左侧「API Key管理」
4. 点击「创建新的API Key」
5. 复制 Key 并添加到 GitHub Secrets 中，名称设为 `BAILIAN_API_KEY`
6. 默认使用 DeepSeek-V3 模型（推荐），也可选择 qwen-plus 等其他模型

**如何获取 Google Gemini API Key（可选，备用）：**

1. 访问 https://makersuite.google.com/app/apikey
2. 使用 Google 账号登录
3. 点击「Create API Key」
4. 复制 Key 并添加到 GitHub Secrets 中，名称设为 `GEMINI_API_KEY`

#### 第三步：启用GitHub Actions

1. 点击仓库顶部 **Actions** 标签
2. 点击绿色的 **"I understand my workflows, go ahead and enable them"** 按钮
3. 启用后，工作流就可以运行了

#### 第四步：手动测试运行

1. 点击 **Actions** 标签
2. 左侧选择 **"Daily Stock Analysis"** 工作流
3. 点击右侧 **"Run workflow"** 下拉按钮
4. 点击绿色的 **"Run workflow"** 按钮
5. 等待运行完成（约2-5分钟）

#### 第五步：查看结果

1. 点击运行的workflow（蓝色链接）
2. 查看运行日志，确认分析完成
3. 检查你的通知渠道（Telegram/钉钉等）是否收到推送
4. 也可以在Artifacts中下载分析报告

**完成！** 🎉

系统将在**每周二到周六早上5:00（北京时间）自动运行**（美股周一到周五收盘后）。

---

### 方式二：本地运行

```bash
# 1. 克隆项目
git clone https://github.com/ZenKaiii/ai-stock-analyst.git
cd ai-stock-analyst

# 2. 安装依赖
pip install -r requirements.txt
pip install -e .

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加 GEMINI_API_KEY

# 4. 运行分析
python -m ai_stock_analyst.main --stocks AAPL,TSLA

# 5. 启动Web界面（可选）
python -m ai_stock_analyst.web.app
# 打开 http://localhost:8000
```

---

### 方式三：Docker部署

```bash
# 1. 启动所有服务
docker-compose up -d

# 2. 查看日志
docker-compose logs -f

# 3. 停止服务
docker-compose down
```

---

## 📋 项目结构

```
ai-stock-analyst/
├── ai_stock_analyst/        # 主程序包
│   ├── config/              # 配置管理
│   ├── database/            # SQLite数据库
│   ├── data/                # 股票数据获取(yfinance)
│   ├── rss/                 # RSS新闻 + 社媒抓取
│   ├── llm/                 # LLM路由(Gemini+百炼)
│   ├── agents/              # AI分析Agent系统
│   ├── notification/        # 通知推送(多平台)
│   └── main.py              # CLI入口
├── .github/
│   └── workflows/
│       └── daily-analysis.yml   # GitHub Actions配置
├── docs/
│   └── README_EN.md         # 英文文档
├── docker-compose.yml
├── Dockerfile
├── .env.example             # 环境变量模板
├── requirements.txt         # Python依赖
├── pyproject.toml
└── README.md                # 本文档
```

---

## 📐 Spec 模式开发（Spec Kit）

本项目已落地一套可执行的 Spec 文档骨架，用于按需求驱动推进多 Agent 升级。

### 已创建文件

- `.specify/memory/constitution.md`
- `specs/001-risk-aware-multi-agent-upgrade/spec.md`
- `specs/001-risk-aware-multi-agent-upgrade/plan.md`
- `specs/001-risk-aware-multi-agent-upgrade/tasks.md`

### 推荐执行顺序

1. 先读宪章：`constitution.md`（定义硬约束）
2. 再确认需求：`spec.md`（定义目标与验收）
3. 按实施计划：`plan.md`（按里程碑推进）
4. 逐项落地：`tasks.md`（按任务执行并打勾）

### 对应当前升级方向

- 多角色 Agent（Fundamental/Bull/Bear/Risk）
- 风控闸门（Risk Gate）
- 技术指标扩展（RSI/MACD/ATR）
- 结构化事件源 + 回测报告

---

## 🔄 回测命令（Backtest）

使用内置回测脚本快速评估策略表现：

```bash
python scripts/backtest_strategy.py --symbols SPY,QQQ --period 2y --output-dir reports
```

输出文件：
- `reports/backtest_*.md`
- `reports/backtest_*.json`

---

## 🔧 详细配置说明

### 环境变量配置（.env文件）

```bash
# ===========================================
# 数据库配置（SQLite - 零配置，无需修改）
# ===========================================
DATABASE_URL=sqlite:///./data/stock_analyzer.db

# ===========================================
# LLM配置 - 阿里云百炼（主要推荐）
# 获取地址: https://bailian.console.aliyun.com/
# 默认模型: DeepSeek-V3（推荐）
# ===========================================
BAILIAN_API_KEY=sk-your-api-key-here
BAILIAN_REGION=beijing
BAILIAN_MODEL=deepseek-v3

# ===========================================
# LLM配置 - Google Gemini（备用）
# 获取地址: https://makersuite.google.com/app/apikey
# ===========================================
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash

# LLM路由策略（自动故障转移）
LLM_PRIMARY=bailian
LLM_FALLBACK=gemini

# ===========================================
# 股票列表（英文逗号分隔）
# ===========================================
STOCK_LIST=AAPL,TSLA,NVDA,MSFT,GOOGL,AMZN,META

# ===========================================
# 通知渠道配置（至少配置一个）
# ===========================================

# Telegram（推荐）
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# 钉钉
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx

# 飞书
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx

# 企业微信
WECHAT_WORK_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
```

### GitHub Actions定时配置

默认配置：每周二到周六早上5:00运行（美股收盘后）

如需修改时间，编辑 `.github/workflows/daily-analysis.yml`：

```yaml
on:
  schedule:
    # 格式: 分钟 小时 日 月 星期 (UTC时间)
    # 北京时间5:00 = UTC 21:00（前一天）
    - cron: '0 21 * * 1-5'  # 周一到周五UTC 21:00
```

**时间对照表：**
- UTC 21:00 = 北京时间次日 5:00
- UTC 13:00 = 北京时间 21:00
- UTC 00:00 = 北京时间 8:00

---

## 🆕 新功能：热门股票发现与持仓分析

### 1. 热门股票发现 (--discover)

从新闻和社交媒体中自动发现潜在热门股票：

```bash
# 本地运行
stock-analyze --discover
```

**GitHub Actions 使用：**

1. 手动触发：Actions → Daily Stock Analysis → Run workflow → 选择 mode 为 "discover"

2. 定时任务：在 workflow 中添加新的 schedule

```yaml
# 添加定时发现热门股票（每周六）
- cron: '0 21 * * 6'
```

**功能说明：**
- 扫描所有RSS新闻源
- 提取股票代码和情绪关键词
- 计算看涨评分 + 综合评分（情绪+趋势+来源多样性）
- 推荐Top 5热门股票

---

### 2. 持仓分析 (--portfolio)

管理并分析你的持仓：

```bash
# 添加持仓
stock-analyze --add-holding NVDA,10,180.50
stock-analyze --add-holding AAPL,5,150.00

# 列出所有持仓
stock-analyze --list-holdings

# 分析持仓
stock-analyze --portfolio
```

**GitHub Actions 使用：**

1. **配置持仓 Secrets：**

在 GitHub Secrets 中添加 `PORTFOLIO_HOLDINGS`，格式为 JSON：

```json
[{"symbol": "NVDA", "shares": 10, "avg_cost": 180.50}, {"symbol": "AAPL", "shares": 5, "avg_cost": 150.00}]
```

2. **手动触发：**

Actions → Daily Stock Analysis → Run workflow → 选择 mode 为 "portfolio"

3. **定时任务：** 添加新的 schedule

**功能说明：**
- 添加/更新持仓
- 获取实时价格
- 计算未实现盈亏
- 风险分析（集中度、亏损过多等）
- 操作建议（卖出锁定利润、止损等）

### 3. IBKR持仓同步（美国区可用）

支持从 IBKR TWS/Gateway 直接拉取持仓并写入本地持仓表（可再接 `--portfolio` 自动分析）。

```bash
# 先安装任一SDK（推荐 ib_async）
pip install ib_async
# 或
pip install ib_insync

# 仅同步
stock-analyze --sync-ibkr-holdings

# 同步后立即做持仓分析
stock-analyze --sync-ibkr-holdings --portfolio
```

需要在 `.env` 配置：
- `IBKR_HOST`（默认 `127.0.0.1`）
- `IBKR_PORT`（默认 `7497`，实盘常见 `7496`）
- `IBKR_CLIENT_ID`（默认 `21`）
- `IBKR_ACCOUNT`（可选）

参数含义：
- `IBKR_HOST`: IBKR TWS/Gateway 所在主机地址（本机一般是 `127.0.0.1`）。
- `IBKR_PORT`: API 端口，`7497` 通常是 Paper，`7496` 通常是 Live。
- `IBKR_CLIENT_ID`: API 客户端连接编号，用于区分不同脚本连接（避免冲突）。
- `IBKR_ACCOUNT`: 可选账户过滤（多账户场景下指定一个账户）。

GitHub Actions 说明：
- workflow 已新增 `mode=ibkr_portfolio`，会执行“同步持仓 + 直接分析”。
- 需要在仓库 Secrets 配置 `IBKR_HOST/IBKR_PORT/IBKR_CLIENT_ID/IBKR_ACCOUNT`。
- workflow 现已启用严格模式：若 IBKR 同步失败会直接失败，便于排查配置问题。
- 若使用 GitHub 官方托管 runner，`127.0.0.1` 指向的是 runner 自己，不是你本地电脑。要成功连接 IBKR，通常需要：
  1. 自建 `self-hosted runner`（与你 TWS/Gateway 在同一网络），或
  2. 可公网访问且安全加固的 IBKR Gateway 服务。

如何确认参数（TWS/Gateway）：
1. 打开 TWS / IB Gateway。
2. 进入 API 设置页面（常见路径：`Configure -> API -> Settings`）。
3. 确认以下项：
   - 启用 API 连接（Enable ActiveX and Socket Clients）。
   - 记录 Socket Port（Paper 常见 7497，Live 常见 7496）。
   - 若做白名单，确保 runner 所在 IP 在 Trusted IPs。
4. `clientId` 由你自己定义（如 21），同一时刻避免与其他脚本重复。

官方参考：
- IBKR API 文档入口：<https://ibkrcampus.com/campus/ibkr-api-page/>
- Python SDK（ib_async）：<https://github.com/ib-api-reloaded/ib_async>

---

### GitHub Actions 多模式运行

workflow 现在支持三种模式：

| Mode | 说明 | 触发方式 |
|------|------|---------|
| `analyze` | 分析 STOCK_LIST 中的股票（默认） | 定时或手动 |
| `discover` | 发现热门股票 | 手动选择 mode |
| `portfolio` | 分析持仓 | 手动选择 mode |

**手动触发时选择 mode：**

```
Actions → Daily Stock Analysis → Run workflow
→ Mode: 选择 analyze/discover/portfolio
→ 点击 Run workflow
```

---

## 📱 通知效果示例

### Telegram推送

```
🟢 AAPL 分析结果

信号: BUY
置信度: 78%
建议入场价: $185.50
止损价: $176.23
目标价: $204.05

分析摘要:
技术面显示多头排列，MACD金叉，RSI在健康区间...

---
AI Stock Analyzer
```

### 钉钉/飞书推送

钉钉已优化为移动端友好的纯文本换行格式（避免长段挤成一行）；飞书/企业微信继续使用 markdown 卡片。

通知包含：
- 📊 分析结果摘要
- 🎯 买卖信号
- 💰 建议价格（入场/止损/目标）
- 📈 技术面分析要点
- 📰 相关新闻摘要

---

## 💡 为什么使用SQLite？

本项目使用 **SQLite** 而非PostgreSQL，优势如下：

1. **零配置** - 无需安装和配置数据库服务器
2. **GitHub Actions友好** - 在CI/CD环境中无缝运行
3. **零成本** - 不需要外部数据库服务
4. **便携** - 单文件数据库，易于备份
5. **足够用** - 对于每日分析任务，性能完全足够

**数据持久化策略：**
- 每次GitHub Actions运行创建全新的数据库
- 分析结果推送到通知渠道（Telegram/钉钉等）作为永久记录
- 报告文件作为Artifacts上传（保留30天）

---

## 🔍 故障排查

### GitHub Actions运行失败

1. **检查Secrets配置**
   - 确认 `GEMINI_API_KEY` 已正确设置（必需）
   - 确认没有多余的空格或换行符
   - 可选：配置 `BAILIAN_API_KEY` 作为备用

2. **查看运行日志**
   - 进入Actions → 点击失败的workflow
   - 查看具体的错误信息

3. **本地测试**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   python -m ai_stock_analyst.main --stocks AAPL
   ```

### 收不到通知

1. **检查通知配置状态**
   ```bash
   python -m src.main
   # 查看输出的通知渠道配置状态
   ```

2. **确认Secrets已设置**
   - 至少配置一个通知渠道
   - Token/Key不要有多余空格

3. **测试单个渠道**
   - Telegram: 先给Bot发消息，确认Bot能收到
   - 钉钉/飞书: 检查Webhook地址是否正确

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

---

## 📄 许可证

MIT License

---

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

如有问题，欢迎提交 [Issue](https://github.com/ZenKaiii/ai-stock-analyst/issues)
