"""油气生产日报系统 - FastAPI 应用入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import get_connection, init_db
from .routers import production
from .services.seed_service import seed_initial_data_if_empty


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用启动时建库并写入演示初始数据。"""
    init_db()
    conn = get_connection()
    try:
        seed_initial_data_if_empty(conn)
    finally:
        conn.close()
    yield


app = FastAPI(
    title="油气生产日报系统 API",
    description="油气生产数据管理与日报自动生成（演示项目，数据均为模拟数据）",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(production.router, prefix="/api")


@app.get("/health", tags=["system"])
def health():
    """健康检查。"""
    return {"status": "ok"}
