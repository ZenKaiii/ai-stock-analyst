"""
数据库包初始化

导出数据库相关类和函数
"""
from .connection import Database, get_db

__all__ = ["Database", "get_db"]
