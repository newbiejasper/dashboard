# -*- coding: utf-8 -*-
"""DDYL DataSource API - 多源数据源连接管理"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.datasource import DataSource
from app.schemas import (
    DataSourceCreate, DataSourceUpdate, DataSourceResponse, MessageResponse
)

router = APIRouter(prefix="/datasources", tags=["数据源管理"])


@router.get("/", response_model=list[DataSourceResponse])
async def list_datasources(
    source_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取数据源列表"""
    query = select(DataSource).where(DataSource.owner_id == current_user.id)
    if source_type:
        query = query.where(DataSource.source_type == source_type)
    query = query.order_by(DataSource.updated_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/types")
async def get_source_types():
    """获取支持的数据源类型列表"""
    return {
        "types": [
            {"key": "mysql", "name": "MySQL", "category": "OLTP数据库", "icon": "mysql"},
            {"key": "clickhouse", "name": "ClickHouse", "category": "OLAP/数仓", "icon": "clickhouse"},
            {"key": "starrocks", "name": "StarRocks", "category": "OLAP/数仓", "icon": "starrocks"},
            {"key": "postgresql", "name": "PostgreSQL", "category": "OLTP数据库", "icon": "postgres"},
            {"key": "excel", "name": "Excel", "category": "文件数据源", "icon": "excel"},
            {"key": "csv", "name": "CSV", "category": "文件数据源", "icon": "csv"},
            {"key": "txt", "name": "TXT", "category": "文件数据源", "icon": "txt"},
            {"key": "api", "name": "API接口", "category": "API数据源", "icon": "api"},
            {"key": "kafka", "name": "Kafka", "category": "大数据平台", "icon": "kafka"},
            {"key": "redis", "name": "Redis", "category": "大数据平台", "icon": "redis"},
        ],
        "connection_modes": [
            {"key": "direct", "name": "直连模式", "desc": "实时查询数据库"},
            {"key": "local_cache", "name": "本地缓存模式", "desc": "Doris引擎缓存，秒级响应"},
        ]
    }


@router.post("/", response_model=DataSourceResponse)
async def create_datasource(
    ds_in: DataSourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建数据源连接"""
    datasource = DataSource(
        name=ds_in.name,
        description=ds_in.description,
        source_type=ds_in.source_type,
        connection_mode=ds_in.connection_mode,
        config=ds_in.config,
        owner_id=current_user.id,
    )
    db.add(datasource)
    await db.flush()
    await db.refresh(datasource)
    return datasource


@router.get("/{datasource_id}", response_model=DataSourceResponse)
async def get_datasource(
    datasource_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取数据源详情"""
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == datasource_id,
            DataSource.owner_id == current_user.id,
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="DataSource not found")
    return ds


@router.put("/{datasource_id}", response_model=DataSourceResponse)
async def update_datasource(
    datasource_id: int,
    ds_in: DataSourceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新数据源"""
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == datasource_id,
            DataSource.owner_id == current_user.id,
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="DataSource not found")
    for field, value in ds_in.dict(exclude_unset=True).items():
        setattr(ds, field, value)
    await db.flush()
    await db.refresh(ds)
    return ds


@router.delete("/{datasource_id}", response_model=MessageResponse)
async def delete_datasource(
    datasource_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除数据源"""
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == datasource_id,
            DataSource.owner_id == current_user.id,
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="DataSource not found")
    await db.delete(ds)
    return MessageResponse(message="DataSource deleted")


@router.post("/{datasource_id}/test")
async def test_connection(
    datasource_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """测试数据源连接"""
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == datasource_id,
            DataSource.owner_id == current_user.id,
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="DataSource not found")
    # TODO: Actual connection test logic per source_type
    return {"status": "success", "message": f"Connection to {ds.name} successful"}
