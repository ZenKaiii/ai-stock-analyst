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
| 🧩 多Agent协作 | 研究员分工 | Macro + Technical + Liquidity + Fundamental + Bull/Bear + Risk 协同决策 |
| 🛡️ 风控 | Risk Gate | 高波动/事件窗口/数据质量异常时自动降级 BUY 信号 |
| 🌍 地缘政治 | 宏观事件风控 | 纳入地缘政治与Trump政策动态对美股冲击评估 |
| 📡 新闻 | RSS+结构化事件 | SeekingAlpha/WSJ/CNBC/NYT/Investing/NewsMinimalist + Fed/SEC/CFTC/IMF/CISA |
| 🐦 社媒 | 情绪监控 | Twitter/X和Reddit讨论情绪分析 |
| 🧠 LLM | 双模型支持 | 阿里云百炼 DeepSeek(主要) + Google Gemini(备用) |
| 📱 推送 | 多渠道通知 | Telegram、钉钉、飞书、企业微信 |
| ⚡ 自动化 | GitHub Actions | 定时执行，零成本运行 |

### 与“8-Agent推送系统”思路对照

本项目已落地并可持续演进的映射如下：
- `Macro Regime` → `MacroRegimeAgent`（QQQ/VIX + 宏观政策关键词）
- `Liquidity & Market Quality` → `LiquidityQualityAgent`（成交额/活跃度/波动/跳空）
- `Fundamental Stability` → `FundamentalAnalyst`（财报稳定性评分、增长与杠杆）
- `News Catalyst` → `NewsAnalyst` + 结构化事件源（含地缘政治/财报监控）
- `Risk & Portfolio Control` → `RiskManager` + `PortfolioManager`（风险闸门 + 仓位）

尚未完全覆盖但已预留扩展位：
- `Sector Rotation`（板块轮动）
- `Flow & Derivatives`（期权/资金流）
- `ICT Structure`（更细粒度市场结构）

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
- `specs/002-beginner-friendly-dashboard-and-ibkr-onboarding/spec.md`
- `specs/002-beginner-friendly-dashboard-and-ibkr-onboarding/plan.md`
- `specs/002-beginner-friendly-dashboard-and-ibkr-onboarding/tasks.md`
- `specs/003-mobile-template-ibkr-cpapi-and-agent-upgrade/spec.md`
- `specs/003-mobile-template-ibkr-cpapi-and-agent-upgrade/plan.md`
- `specs/003-mobile-template-ibkr-cpapi-and-agent-upgrade/tasks.md`
- `specs/004-dingtalk-universe-discovery-and-ibkr-playbook/spec.md`
- `specs/004-dingtalk-universe-discovery-and-ibkr-playbook/plan.md`
- `specs/004-dingtalk-universe-discovery-and-ibkr-playbook/tasks.md`
- `specs/005-universe-news-ibkr-hosted-feasibility/spec.md`
- `specs/005-universe-news-ibkr-hosted-feasibility/plan.md`
- `specs/005-universe-news-ibkr-hosted-feasibility/tasks.md`

### 推荐执行顺序

1. 先读宪章：`constitution.md`（定义硬约束）
2. 再确认需求：`spec.md`（定义目标与验收）
3. 按实施计划：`plan.md`（按里程碑推进）
4. 逐项落地：`tasks.md`（按任务执行并打勾）

### 对应当前升级方向

- 多角色 Agent（Macro/Liquidity/Fundamental/Bull/Bear/Risk）
- 风控闸门（Risk Gate）
- 技术指标扩展（RSI/MACD/ATR）
- 结构化事件源 + 回测报告
- IBKR 双通道接入（Socket + CPAPI）

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

从“全市场候选池”中自动发现潜在热门股票（Top1 + 20备选）：

```bash
# 本地运行
stock-analyze --discover

# 可调参数（全市场扫描）
stock-analyze --discover \
  --discover-universe-size 0 \
  --discover-prefilter-size 120 \
  --discover-final-size 21 \
  --discover-max-news 180
```

**GitHub Actions 使用：**

1. 手动触发：Actions → Daily Stock Analysis → Run workflow → 选择 mode 为 "discover"

2. 定时任务：在 workflow 中添加新的 schedule

```yaml
# 添加定时发现热门股票（每周六）
- cron: '0 21 * * 6'
```

**功能说明：**
- 扫描美股候选池（NASDAQ + NYSE + NYSE American + Arca 等）+ RSS 新闻源
- 初筛：价格/流动性/动量（预筛得分）
- 评分：技术面 + 财报稳定性 + 新闻解读 + 预筛分 + 新闻源质量分
- 输出：Top1 推荐 + 20只备选（含扫描/初筛/评分/交易所覆盖统计）
- 每只候选股输出：公司做什么、行业/板块、新闻事件概述、为什么利好/利空、入场/目标参考

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

支持两条官方路径：
- `socket`：TWS/Gateway Socket API（`ib_async` / `ib_insync`）
- `cpapi`：Client Portal API（通过 Client Portal Gateway + 浏览器会话）

同步后都会写入本地持仓表（可再接 `--portfolio` 自动分析）。

```bash
# socket 模式需安装任一SDK（推荐 ib_async）
pip install ib_async
# 或
pip install ib_insync

# 仅同步（默认 auto 模式，会先尝试 socket 再尝试 cpapi）
# export IBKR_API_MODE=auto
stock-analyze --sync-ibkr-holdings

# 连接自检（推荐先跑）
stock-analyze --ibkr-check

# 仅同步
# export IBKR_API_MODE=cpapi
# export IBKR_CPAPI_BASE_URL=https://localhost:5000/v1/api
# export IBKR_CPAPI_VERIFY_SSL=false
# stock-analyze --sync-ibkr-holdings

# 同步后立即做持仓分析
stock-analyze --sync-ibkr-holdings --portfolio
```

需要在 `.env` 配置：
- `IBKR_API_MODE`（`auto/socket/cpapi`，默认 `auto`）
- `IBKR_HOST`（默认 `127.0.0.1`）
- `IBKR_PORT`（默认 `7497`，实盘常见 `7496`）
- `IBKR_CLIENT_ID`（默认 `21`）
- `IBKR_ACCOUNT`（可选）
- `IBKR_CPAPI_BASE_URL`（默认 `https://localhost:5000/v1/api`）
- `IBKR_CPAPI_VERIFY_SSL`（默认 `false`）
- `IBKR_CPAPI_TIMEOUT`（默认 `12`）

参数含义：
- `IBKR_API_MODE`: 连接模式；`socket` 走 TWS/Gateway，`cpapi` 走 Client Portal API。
- `IBKR_HOST`: IBKR TWS/Gateway 所在主机地址（本机一般是 `127.0.0.1`）。
- `IBKR_PORT`: API 端口，`7497` 通常是 Paper，`7496` 通常是 Live。
- `IBKR_CLIENT_ID`: API 客户端连接编号，用于区分不同脚本连接（避免冲突）。
- `IBKR_ACCOUNT`: 可选账户过滤（多账户场景下指定一个账户）。
- `IBKR_CPAPI_BASE_URL`: Client Portal Gateway API 地址（默认本机 `5000`）。

GitHub Actions 说明：
- workflow 已新增 `mode=ibkr_portfolio`，会执行“同步持仓 + 直接分析”。
- 需要在仓库 Secrets 配置 `IBKR_API_MODE` 及对应参数（socket 或 cpapi）。
- workflow 现已启用严格模式：若 IBKR 同步失败会直接失败，便于排查配置问题。
- workflow 新增前置校验：`IBKR_API_MODE=cpapi` 且 `IBKR_CPAPI_BASE_URL` 指向 `localhost/127.0.0.1` 时，`github-hosted runner` 会直接失败并提示改用 self-hosted runner。
- 若使用 GitHub 官方托管 runner，`127.0.0.1` 指向的是 runner 自己，不是你本地电脑。要成功连接 IBKR，通常需要：
  1. 自建 `self-hosted runner`（与你 TWS/Gateway 或 CP Gateway 同机/同网段），或
  2. 可公网访问且安全加固的网关服务（不推荐给新手）。

如何确认参数（TWS/Gateway）：
1. 打开 TWS / IB Gateway。
2. 进入 API 设置页面（常见路径：`Configure -> API -> Settings`）。
3. 确认以下项：
   - 启用 API 连接（Enable ActiveX and Socket Clients）。
   - 记录 Socket Port（Paper 常见 7497，Live 常见 7496）。
   - 若做白名单，确保 runner 所在 IP 在 Trusted IPs。
4. `clientId` 由你自己定义（如 21），同一时刻避免与其他脚本重复。

#### IBKR API 新手说明（按官方文档）

如果你的目标只是“读取持仓”，两条路径都可用：

1. **Socket API（TWS/Gateway）**
- 不需要单独申请 API Token。
- 鉴权依赖你已经登录的 TWS/IB Gateway 会话。
- 只要 `host + port + clientId` 正确，且 API 开关打开，即可读取持仓。

2. **Client Portal Web API (CPAPI)**
- 需要运行 Client Portal Gateway（本地常见 `https://localhost:5000`）。
- 需要浏览器登录并保持认证会话。
- 官方文档强调会话/认证约束，不是“只填 API Key 永久可用”模式。
- 常见读取持仓端点：`/portfolio/accounts`、`/portfolio/{accountId}/positions`。

**你这种“只有网页端和 mobile、没有 TWS/Gateway”的情况，最适合路径：**
- 短期（最现实）：部署 **Client Portal Gateway + self-hosted runner**，用 `IBKR_API_MODE=cpapi` 做持仓拉取与分析。
- 中期（自动化交易）：在 CPAPI 会话管理稳定后，再接入下单端点做“交易执行层”。

可行性结论（直接回答）：
- `github-hosted runner + 仅 web/mobile + 本地 localhost CP Gateway`：不可行（runner 无法访问你本地网关，且 CPAPI 会话需浏览器登录）。
- `self-hosted runner + CP Gateway`：可行（推荐给当前账号形态）。

当前仓库已支持 `cpapi` 模式，适配上述路径。

#### 参考项目 thetagang 的可借鉴点

参考项目：<https://github.com/brndnmtthws/thetagang>

从实现上看，thetagang 主要采用：
- `ib_async` 作为核心 IB SDK；
- `IBC + Watchdog` 管理 TWS/Gateway 生命周期与重连；
- `--dry-run` 和订单状态跟踪，降低实盘误操作风险。

对我们的启发：
1. 交易自动化阶段建议优先走 `socket`（TWS/Gateway），因为下单稳定性和事件回调更成熟。
2. 仅持仓读取/账户观测阶段，`cpapi` 依然是 web/mobile-only 用户更现实路径。
3. 上线交易前应先实现 `dry-run`、订单审计、失败重试、风控闸门联动（可作为下一期 SDD 任务）。

#### 新闻源参考项目借鉴（situation-monitor / News Minimalist）

借鉴点已落地到本项目：
1. 多源聚合思路：扩展到 NYT Business/Economy、Investing.com、News Minimalist、CISA 等；
2. 质量与鲁棒性思路：推荐评分中加入“新闻源质量分”（source quality）和来源多样性；
3. 小白可读性思路：热门发现结果保留“扫描 -> 初筛 -> 评分 -> 推荐”全流程统计，且给出 Top1 + 20备选。

官方参考：
- IBKR API 文档入口：<https://ibkrcampus.com/campus/ibkr-api-page/>
- IBKR 中国站 API 介绍（你提供的入口）：<https://www.interactivebrokers.com/cn/trading/ib-api.php#api-software>
- TWS API 初始配置（含默认端口 7496/7497）：<https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/#initial-setup>
- Client Portal API 认证说明：<https://ibkrcampus.com/campus/ibkr-api-page/cpapi-v1/>
- Python SDK（ib_async）：<https://github.com/ib-api-reloaded/ib_async>

---

### GitHub Actions 多模式运行

workflow 现在支持四种模式：

| Mode | 说明 | 触发方式 |
|------|------|---------|
| `analyze` | 分析 STOCK_LIST 中的股票（默认） | 定时或手动 |
| `discover` | 发现热门股票 | 手动选择 mode |
| `portfolio` | 分析持仓 | 手动选择 mode |
| `ibkr_portfolio` | 同步 IBKR 持仓并分析 | 手动选择 mode |

**手动触发时选择 mode：**

```
Actions → Daily Stock Analysis → Run workflow
→ Mode: 选择 analyze/discover/portfolio/ibkr_portfolio
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

钉钉/飞书/企业微信均使用 markdown 结构化消息。钉钉端已针对移动端做了标题去重、长消息分段和单层列表优化。
钉钉机器人文档（markdown 消息类型）可参考：<https://open.dingtalk.com/document/robots/custom-robot-access>
结合钉钉移动端渲染行为，项目对粗体/行内代码做了稳定性降级（避免出现残留 `*` 或错位）。

通知包含：
- 📊 分析结果摘要
- 🎯 买卖信号
- 📈 综合评分（0-100）
- 💰 建议价格（入场/止损/目标）
- 📈 技术面分析要点（手机端卡片化）
- 🌍 宏观环境（QQQ/VIX/政策事件）
- 💧 流动性质量（成交额/活跃度/波动）
- 🧾 财报与基本面稳定性
- 📰 新闻“概要+解读”
- 📚 指标小白解释（RSI/MACD/ATR）
- ✅ 分场景操作建议（空仓/持仓）

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
