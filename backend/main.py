# -*- coding: utf-8 -*-
"""
DDYL BI Platform - Application Entry Point
人人可用的数据可视化神器
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup/shutdown"""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Auto-migrate: add new dataset columns if they don't exist
        await conn.run_sync(_migrate_dataset_columns)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.TEMPLATE_DIR, exist_ok=True)
    yield
    # Shutdown
    await engine.dispose()


def _migrate_dataset_columns(conn):
    """Add new dataset columns for SQLite (ignores if already exist)"""
    import sqlalchemy as sa
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("datasets")]
    new_columns = {
        "dimensions_config": "JSON",
        "measures_config": "JSON",
        "drill_down_config": "JSON",
        "filter_fields": "JSON",
    }
    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            conn.execute(sa.text(f"ALTER TABLE datasets ADD COLUMN {col_name} {col_type}"))


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="人人可用的数据可视化神器 - BI商业智能数据分析平台",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/media", StaticFiles(directory="media"), name="media")

# API Routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
