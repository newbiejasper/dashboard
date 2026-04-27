# -*- coding: utf-8 -*-
"""DDYL Dataset API - 数据集管理"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.datasource import Dataset
from app.schemas import DatasetCreate, DatasetUpdate, DatasetResponse, MessageResponse

import pandas as pd
import json
import os
from datetime import datetime

router = APIRouter(prefix="/datasets", tags=["数据集管理"])


@router.get("/", response_model=list[DatasetResponse])
async def list_datasets(
    dataset_type: Optional[str] = None,
    datasource_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取数据集列表"""
    query = select(Dataset).where(Dataset.owner_id == current_user.id)
    if dataset_type:
        query = query.where(Dataset.dataset_type == dataset_type)
    if datasource_id:
        query = query.where(Dataset.datasource_id == datasource_id)
    query = query.order_by(Dataset.updated_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=DatasetResponse)
async def create_dataset(
    ds_in: DatasetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建数据集"""
    dataset = Dataset(
        name=ds_in.name,
        description=ds_in.description or "",
        dataset_type=ds_in.dataset_type,
        datasource_id=ds_in.datasource_id,
        source_table=ds_in.source_table,
        sql_query=ds_in.sql_query,
        fields_config=ds_in.fields_config or [],
        dimensions_config=ds_in.dimensions_config or [],
        measures_config=ds_in.measures_config or [],
        drill_down_config=ds_in.drill_down_config or [],
        filter_fields=ds_in.filter_fields or [],
        transformations=ds_in.transformations or {},
        sync_config=ds_in.sync_config or {},
        owner_id=current_user.id,
    )
    db.add(dataset)
    await db.flush()
    await db.refresh(dataset)
    return dataset


@router.post("/upload", response_model=DatasetResponse)
async def upload_file_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传文件创建数据集 (Excel/CSV/TXT)"""
    upload_dir = "media/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Parse file with pandas
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file.filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)
    elif file.filename.endswith(".txt"):
        df = pd.read_csv(file_path, sep="\t")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Build fields config
    fields_config = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        field_type = "number" if "float" in dtype or "int" in dtype else "string"
        if "datetime" in dtype:
            field_type = "date"
        fields_config.append({
            "name": col,
            "type": field_type,
            "original_type": dtype,
            "alias": col,
        })

    dataset = Dataset(
        name=name or file.filename.rsplit(".", 1)[0],
        description=f"Uploaded from {file.filename}",
        dataset_type="file",
        fields_config=fields_config,
        transformations={},
        data_sample=json.loads(df.head(100).to_json(orient="records", force_ascii=False)),
        row_count=len(df),
        is_synced=True,
        last_sync_at=datetime.utcnow(),
        owner_id=current_user.id,
    )
    db.add(dataset)
    await db.flush()
    await db.refresh(dataset)
    return dataset


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取数据集详情"""
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.owner_id == current_user.id,
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return ds


@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: int,
    ds_in: DatasetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新数据集"""
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.owner_id == current_user.id,
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    for field, value in ds_in.dict(exclude_unset=True).items():
        setattr(ds, field, value)
    await db.flush()
    await db.refresh(ds)
    return ds


@router.delete("/{dataset_id}", response_model=MessageResponse)
async def delete_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除数据集"""
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.owner_id == current_user.id,
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    await db.delete(ds)
    return MessageResponse(message="Dataset deleted")


@router.post("/{dataset_id}/query")
async def query_dataset(
    dataset_id: int,
    dimensions: list = [],
    measures: list = [],
    filters: list = [],
    sort: list = [],
    limit: int = 1000,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询数据集数据 (OLAP查询引擎)"""
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.owner_id == current_user.id,
        )
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # For uploaded files - return sample data directly
    if ds.dataset_type == "file" and ds.data_sample:
        data = ds.data_sample
        # Apply simple filtering logic
        if filters:
            filtered = []
            for row in data:
                match = True
                for f in filters:
                    field = f.get("field")
                    op = f.get("operator", "eq")
                    val = f.get("value")
                    row_val = row.get(field)
                    if op == "eq" and row_val != val:
                        match = False
                    elif op == "gt" and not (row_val and row_val > val):
                        match = False
                    elif op == "lt" and not (row_val and row_val < val):
                        match = False
                    elif op == "gte" and not (row_val and row_val >= val):
                        match = False
                    elif op == "lte" and not (row_val and row_val <= val):
                        match = False
                    elif op == "ne" and row_val == val:
                        match = False
                if match:
                    filtered.append(row)
            data = filtered

        return {
            "data": data[:limit],
            "total": len(data),
            "fields": ds.fields_config,
        }

    return {
        "data": ds.data_sample or [],
        "total": ds.row_count or 0,
        "fields": ds.fields_config,
    }
