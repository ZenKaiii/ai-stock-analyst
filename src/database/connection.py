"""
SQLite数据库连接管理
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Database:
    """SQLite数据库管理类"""
    
    def __init__(self, database_url: str = None):
        from src.config import get_settings
        
        if database_url:
            # 从URL提取路径 (sqlite:///path/to/db.db)
            self.db_path = database_url.replace("sqlite:///", "")
        else:
            self.db_path = "./data/stock_analyzer.db"
        
        # 确保目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 股票基础信息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    name TEXT,
                    sector TEXT,
                    market_cap INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # 股票价格数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL,
                    change REAL,
                    change_percent REAL,
                    volume INTEGER,
                    market_cap INTEGER,
                    pe_ratio REAL,
                    week_52_high REAL,
                    week_52_low REAL,
                    ma5 REAL,
                    ma20 REAL,
                    trend TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 新闻文章表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    title TEXT NOT NULL,
                    content TEXT,
                    summary TEXT,
                    url TEXT UNIQUE NOT NULL,
                    source TEXT,
                    published_at TIMESTAMP,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sentiment_score REAL,
                    sentiment_label TEXT
                )
            """)
            
            # 社交媒体帖子表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS social_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    symbol TEXT,
                    author TEXT,
                    content TEXT NOT NULL,
                    url TEXT,
                    published_at TIMESTAMP,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    likes INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    sentiment_score REAL,
                    sentiment_label TEXT,
                    is_viral BOOLEAN DEFAULT 0
                )
            """)
            
            # AI分析结果表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    analysis_type TEXT,
                    signal TEXT,
                    confidence REAL,
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
                    entry_price REAL,
                    stop_loss REAL,
                    target_price REAL,
                    position_size TEXT,
                    model_used TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_symbol ON stock_prices(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_time ON stock_prices(fetched_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_symbol ON news_articles(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_social_symbol ON social_posts(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_symbol ON analysis_results(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_time ON analysis_results(created_at)")
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self):
        """获取数据库游标上下文管理器"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise
            finally:
                cursor.close()
    
    def execute(self, query: str, params=None):
        """执行SQL查询"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall() if cursor.description else None
    
    def fetch_one(self, query: str, params=None):
        """获取单条记录"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def fetch_all(self, query: str, params=None):
        """获取所有记录"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def insert(self, query: str, params=None) -> int:
        """插入数据并返回ID"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.lastrowid


# 全局数据库实例（延迟初始化）
_db_instance = None


def get_db() -> Database:
    """获取数据库实例（单例模式）"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
