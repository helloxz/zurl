#!/bin/sh

ARG1=$1

# 数据库路径
DB_PATH="/opt/zurl/app/data/db"

# 检查数据库路径是否存在
exist_db(){
    if [ ! -d "$DB_PATH" ]; then
        mkdir -p "$DB_PATH"
    fi
}

# 启动主进程（Redis 由 docker-compose 等单独启动，或通过 REDIS_HOST 等环境变量连接）
runMain(){
    WORKERS=${WORKERS}
    if [ -z "$WORKERS" ]; then
        WORKERS=1
    fi
    . myenv/bin/activate
    alembic upgrade head
    uvicorn app.main:app --workers ${WORKERS} --host 0.0.0.0 --port 3080
}

if [ -z "$ARG1" ]; then
    exist_db && runMain
elif [ "$ARG1" = "dev" ]; then
    echo "Running in development mode..."
    . myenv/bin/activate
    alembic upgrade head
    uvicorn app.main:app --reload --host 0.0.0.0 --port 3080
else
    echo "Unknown argument: $ARG1"
    echo "Usage: $0 [dev]"
    exit 1
fi
