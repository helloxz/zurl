from typing import Union
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 导入路由
from app.routers.routers import router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.middleware.click import update_click_counts
from fastapi.staticfiles import StaticFiles
from app.utils.migration import run_migrations

# 导入数据库模型
from app.models.sessions import Sessions
from app.models.urls import Urls
from app.models.conn import engine, Base, get_db
from app.config import init, get_config
import os

# 提前初始化以便读取 BASE_URL
init()

def _get_base_path():
    """获取 BASE_URL：优先环境变量 BASE_URL，否则读配置文件。用于非根目录部署，返回不带末尾斜杠的路径。"""
    base = os.environ.get("BASE_URL", "").strip() or ""
    if not base:
        try:
            base = (get_config().get("app") or {}).get("BASE_URL") or ""
        except Exception:
            pass
    base = (base or "").strip().rstrip("/")
    return base if base else ""

BASE_PATH = _get_base_path()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时已执行 init()
    pass
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_click_counts, 'interval', minutes=10)
    scheduler.start()
    print("🕒 调度器已启动，定时任务已添加")
    
    yield
    
    # 关闭时执行（可选）
    scheduler.shutdown()
    print("🛑 调度器已关闭")

# 创建 FastAPI 应用实例
app = FastAPI(lifespan=lifespan)

# 挂载静态文件目录（支持非根目录部署）
if BASE_PATH:
    app.mount(f"{BASE_PATH}/dist", StaticFiles(directory="app/templates/dist"), name="static")
else:
    app.mount("/dist", StaticFiles(directory="app/templates/dist"), name="static")

# 注册中间件
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 将路由添加到应用中（支持非根目录部署）
app.include_router(router, prefix=BASE_PATH)

print("🕒 启动调度器...")