FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# 复制应用代码
COPY src/ ./src/
COPY sql/ ./sql/

# 创建数据目录
RUN mkdir -p /app/data /app/reports

# 环境变量
ENV PYTHONPATH=/app
ENV PORT=8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "-m", "src.web"]
