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
| 📡 新闻 | RSS聚合 | 实时获取Seeking Alpha、MarketWatch等财经新闻 |
| 🐦 社媒 | 情绪监控 | Twitter/X和Reddit讨论情绪分析 |
| 🧠 LLM | 双模型支持 | 阿里云百炼(主要) + Google Gemini(备用) |
| 📱 推送 | 多渠道通知 | Telegram、钉钉、飞书、企业微信 |
| ⚡ 自动化 | GitHub Actions | 定时执行，零成本运行 |

### 技术栈

- **Python 3.11+** - 主要编程语言
- **SQLite** - 嵌入式数据库（零配置）
- **FastAPI** - Web框架
- **阿里云百炼 / Google Gemini** - 大语言模型
- **RSSHub** - RSS聚合服务

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
| `BAILIAN_API_KEY` | 阿里云百炼API Key | [阿里云百炼控制台](https://bailian.console.aliyun.com/) |
| `STOCK_LIST` | 要分析的股票代码 | 如：`AAPL,TSLA,NVDA,MSFT` |

**可选 - 通知渠道（至少配置一个）：**

| Secret名称 | 说明 | 获取方式 |
|-----------|------|----------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | [@BotFather](https://t.me/botfather) 创建机器人 |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | [@userinfobot](https://t.me/userinfobot) 获取 |
| `DINGTALK_WEBHOOK_URL` | 钉钉Webhook | 钉钉群 → 群设置 → 智能群助手 → 添加机器人 → 自定义 |
| `FEISHU_WEBHOOK_URL` | 飞书Webhook | 飞书群 → 设置 → 群机器人 → 添加机器人 |
| `WECHAT_WORK_WEBHOOK_URL` | 企业微信Webhook | 企业微信群 → 群设置 → 添加群机器人 |

**如何获取阿里云百炼API Key：**

1. 访问 https://bailian.console.aliyun.com/
2. 使用阿里云账号登录（没有就注册一个）
3. 点击左侧「API Key管理」
4. 点击「创建新的API Key」
5. 复制Key并添加到GitHub Secrets中

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
pip install -e .

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加API Key

# 4. 运行分析
python -m src.main --stocks AAPL,TSLA

# 5. 启动Web界面（可选）
python -m src.web
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
├── src/
│   ├── config/              # 配置管理
│   ├── database/            # SQLite数据库
│   ├── data/                # 股票数据获取(yfinance)
│   ├── rss/                 # RSS新闻 + 社媒抓取
│   ├── llm/                 # LLM路由(百炼+Gemini)
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
├── pyproject.toml
└── README.md                # 本文档
```

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
# ===========================================
BAILIAN_API_KEY=sk-your-api-key-here
BAILIAN_REGION=singapore
BAILIAN_MODEL=qwen-plus

# ===========================================
# LLM配置 - Google Gemini（备用）
# 获取地址: https://makersuite.google.com/app/apikey
# ===========================================
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro

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

支持Markdown格式，包含：
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
   - 确认 `BAILIAN_API_KEY` 已正确设置
   - 确认没有多余的空格

2. **查看运行日志**
   - 进入Actions → 点击失败的workflow
   - 查看具体的错误信息

3. **本地测试**
   ```bash
   pip install -e .
   python -m src.main --stocks AAPL
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
