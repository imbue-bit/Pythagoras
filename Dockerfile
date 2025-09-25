# 使用官方的 Python 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，防止 Python 写入 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
# 确保 Python 输出是无缓冲的
ENV PYTHONUNBUFFERED 1

# 安装系统依赖 (如果需要，例如编译某些 Python 包)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# 安装 Poetry (推荐的依赖管理工具) 或直接使用 requirements.txt
# 使用 Poetry:
# RUN pip install poetry
# COPY poetry.lock pyproject.toml ./
# RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev

# 使用 requirements.txt (更简单直接):
COPY requirements.txt .
# 如果使用 PostgreSQL，需要 psycopg2-binary
# 如果使用 Redis，需要 redis
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目代码到容器中
COPY . .

# 暴露 FastAPI 运行的端口
EXPOSE 8000

# 容器启动时运行的命令
# 使用 --host 0.0.0.0 使服务可以从容器外部访问
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
