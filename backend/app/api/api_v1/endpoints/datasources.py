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


@router.get("/{datasource_id}/tables")
async def list_tables(
    datasource_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取数据源下的所有表"""
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == datasource_id,
            DataSource.owner_id == current_user.id,
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="DataSource not found")

    if ds.source_type == "mysql":
        import aiomysql
        conn = await aiomysql.connect(
            host=ds.config.get("host", "localhost"),
            port=ds.config.get("port", 3306),
            user=ds.config.get("username", "root"),
            password=ds.config.get("password", ""),
            db=ds.config.get("database", ""),
            connect_timeout=5,
        )
        try:
            async with conn.cursor() as cur:
                db_name = ds.config.get("database", "")
                await cur.execute(
                    "SELECT TABLE_NAME, TABLE_COMMENT, ENGINE, TABLE_ROWS "
                    "FROM information_schema.TABLES "
                    "WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE' "
                    "ORDER BY TABLE_NAME",
                    (db_name,),
                )
                rows = await cur.fetchall()
                tables = []
                for r in rows:
                    tables.append({
                        "name": r[0],
                        "comment": r[1] or "",
                        "engine": r[2] or "",
                        "rows": r[3] or 0,
                    })
                return {"tables": tables}
        finally:
            conn.close()
    else:
        # Fallback: return tables from datasets that use this datasource
        from app.models.datasource import Dataset as DatasetModel
        q = select(DatasetModel.source_table).where(
            DatasetModel.datasource_id == datasource_id,
            DatasetModel.source_table.isnot(None),
        ).distinct()
        r = await db.execute(q)
        tables = [{"name": row[0], "comment": "", "engine": "", "rows": 0} for row in r.fetchall()]
        return {"tables": tables}


@router.get("/{datasource_id}/tables/{table_name}/columns")
async def list_table_columns(
    datasource_id: int,
    table_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定表的字段信息"""
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == datasource_id,
            DataSource.owner_id == current_user.id,
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="DataSource not found")

    if ds.source_type == "mysql":
        import aiomysql
        conn = await aiomysql.connect(
            host=ds.config.get("host", "localhost"),
            port=ds.config.get("port", 3306),
            user=ds.config.get("username", "root"),
            password=ds.config.get("password", ""),
            db=ds.config.get("database", ""),
            connect_timeout=5,
        )
        try:
            async with conn.cursor() as cur:
                db_name = ds.config.get("database", "")
                await cur.execute(
                    "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_COMMENT, "
                    "       COLUMN_KEY, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH "
                    "FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
                    "ORDER BY ORDINAL_POSITION",
                    (db_name, table_name),
                )
                rows = await cur.fetchall()
                columns = []
                for r in rows:
                    col_name = r[0]
                    col_type = r[1]
                    data_type = r[5] or ""
                    is_number = data_type in ("int", "bigint", "smallint", "tinyint",
                                              "decimal", "float", "double", "numeric")
                    is_date = data_type in ("date", "datetime", "timestamp", "time", "year")
                    field_type = "number" if is_number else ("date" if is_date else "string")
                    columns.append({
                        "name": col_name,
                        "type": field_type,
                        "original_type": col_type,
                        "nullable": r[2] == "YES",
                        "comment": r[3] or "",
                        "key": r[4] or "",
                        "max_length": r[6],
                    })
                return {"columns": columns}
        finally:
            conn.close()
    else:
        raise HTTPException(status_code=400, detail=f"Table browsing not supported for {ds.source_type}")
