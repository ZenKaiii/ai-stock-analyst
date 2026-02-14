"""
配置管理模块
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 数据库配置 - SQLite（适合GitHub Actions和本地运行）
    DATABASE_URL: str = "sqlite:///./data/stock_analyzer.db"
    
    # LLM配置 - 阿里云百炼（主要推荐）
    BAILIAN_API_KEY: str = ""
    BAILIAN_REGION: str = "beijing"
    BAILIAN_MODEL: str = "deepseek-v3"

    # LLM配置 - Google Gemini（备用）
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # LLM路由策略 - 默认使用百炼 DeepSeek，Gemini 作为备用
    LLM_PRIMARY: str = "bailian"
    LLM_FALLBACK: str = "gemini"
    
    # RSS配置
    RSSHUB_URLS: List[str] = ["https://rsshub.app", "https://rsshub.rssforever.com"]
    
    # 通知配置
    GITHUB_TOKEN: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # 股票列表
    STOCK_LIST: str = "AAPL,TSLA,NVDA,MSFT,GOOGL,AMZN,META"
    
    # 数据保留天数
    DATA_RETENTION_DAYS: int = 30
    
    # Web配置
    WEB_HOST: str = "0.0.0.0"
    WEB_PORT: int = 8000
    WEB_DEBUG: bool = False

    # IBKR API (TWS/Gateway)
    IBKR_API_MODE: str = "auto"
    IBKR_HOST: str = "127.0.0.1"
    IBKR_PORT: int = 7497
    IBKR_CLIENT_ID: int = 21
    IBKR_ACCOUNT: str = ""
    IBKR_CPAPI_BASE_URL: str = "https://localhost:5000/v1/api"
    IBKR_CPAPI_VERIFY_SSL: bool = False
    IBKR_CPAPI_TIMEOUT: int = 12
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def stocks(self) -> List[str]:
        """获取股票列表"""
        return [s.strip() for s in self.STOCK_LIST.split(",") if s.strip()]


# 全局配置实例（延迟初始化）
_settings = None


def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
