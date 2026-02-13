-- sql/init.sql - PostgreSQL数据库初始化
-- 运行: psql -U postgres -f sql/init.sql

-- 创建数据库（如果不存在）
SELECT 'CREATE DATABASE stock_analyzer'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'stock_analyzer')\gexec

\c stock_analyzer;

-- 1. 股票基础信息表
CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100),
    sector VARCHAR(50),
    market_cap BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. 股票价格数据
CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) REFERENCES stocks(symbol),
    price DECIMAL(10, 2),
    change DECIMAL(10, 2),
    change_percent DECIMAL(5, 2),
    volume BIGINT,
    market_cap BIGINT,
    pe_ratio DECIMAL(8, 2),
    week_52_high DECIMAL(10, 2),
    week_52_low DECIMAL(10, 2),
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_symbol_time UNIQUE (symbol, fetched_at)
);

-- 3. RSS新闻源配置
CREATE TABLE IF NOT EXISTS rss_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    source_type VARCHAR(20),
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    last_fetched_at TIMESTAMP,
    fetch_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 新闻文章表
CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES rss_sources(id),
    symbol VARCHAR(10),
    title TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    url TEXT UNIQUE NOT NULL,
    published_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sentiment_score DECIMAL(3, 2),
    sentiment_label VARCHAR(10),
    keywords TEXT[],
    is_processed BOOLEAN DEFAULT FALSE
);

-- 5. 社交媒体帖子表
CREATE TABLE IF NOT EXISTS social_posts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(20) NOT NULL,
    symbol VARCHAR(10),
    author VARCHAR(100),
    content TEXT NOT NULL,
    url TEXT,
    published_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    sentiment_score DECIMAL(3, 2),
    sentiment_label VARCHAR(10),
    is_viral BOOLEAN DEFAULT FALSE
);

-- 6. AI分析结果表
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) REFERENCES stocks(symbol),
    analysis_type VARCHAR(20),
    signal VARCHAR(10),
    confidence DECIMAL(3, 2),
    technical_score INTEGER,
    fundamental_score INTEGER,
    news_score INTEGER,
    social_score INTEGER,
    risk_score INTEGER,
    summary TEXT,
    technical_analysis TEXT,
    fundamental_analysis TEXT,
    news_analysis TEXT,
    social_analysis TEXT,
    risk_factors TEXT[],
    entry_price DECIMAL(10, 2),
    stop_loss DECIMAL(10, 2),
    target_price DECIMAL(10, 2),
    position_size VARCHAR(20),
    model_used VARCHAR(50),
    news_count INTEGER,
    social_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    report_url TEXT
);

-- 7. 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 通知记录表
CREATE TABLE IF NOT EXISTS notification_logs (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analysis_results(id),
    channel VARCHAR(20),
    status VARCHAR(20),
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引优化查询
CREATE INDEX IF NOT EXISTS idx_news_symbol ON news_articles(symbol);
CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_social_symbol ON social_posts(symbol);
CREATE INDEX IF NOT EXISTS idx_social_platform ON social_posts(platform);
CREATE INDEX IF NOT EXISTS idx_analysis_symbol ON analysis_results(symbol);
CREATE INDEX IF NOT EXISTS idx_analysis_created ON analysis_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_prices_symbol_time ON stock_prices(symbol, fetched_at DESC);

-- 插入默认配置（如果不存在）
INSERT INTO system_config (config_key, config_value) VALUES
('stock_list', 'AAPL,TSLA,NVDA,MSFT,GOOGL,AMZN,META'),
('analysis_schedule', '0 5 * * 2-6'),
('rss_update_schedule', '0 */2 * * 1-5'),
('data_retention_days', '30'),
('default_analysis_type', 'full')
ON CONFLICT (config_key) DO NOTHING;

-- 插入默认RSS源
INSERT INTO rss_sources (name, url, source_type, priority) VALUES
('Seeking Alpha', 'https://seekingalpha.com/feed.xml', 'news', 1),
('MarketWatch', 'https://feeds.content.dowjones.io/public/rss/mw_topstories', 'news', 2),
('CNBC', 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114', 'news', 3),
('Investing.com', 'https://www.investing.com/rss/news.rss', 'news', 4),
('Nasdaq', 'https://www.nasdaq.com/feed/rssoutbound?category=Stocks', 'news', 5),
('Reddit WSB', 'https://www.reddit.com/r/wallstreetbets/hot.rss', 'reddit', 3),
('Reddit Stocks', 'https://www.reddit.com/r/stocks/hot.rss', 'reddit', 4)
ON CONFLICT DO NOTHING;

-- 插入监控股票
INSERT INTO stocks (symbol, name, sector) VALUES
('AAPL', 'Apple Inc.', 'Technology'),
('TSLA', 'Tesla Inc.', 'Consumer Cyclical'),
('NVDA', 'NVIDIA Corporation', 'Technology'),
('MSFT', 'Microsoft Corporation', 'Technology'),
('GOOGL', 'Alphabet Inc.', 'Communication Services'),
('AMZN', 'Amazon.com Inc.', 'Consumer Cyclical'),
('META', 'Meta Platforms Inc.', 'Communication Services')
ON CONFLICT (symbol) DO NOTHING;
