# -*- coding: utf-8 -*-
"""DDYL Schemas"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


# ===== Auth =====
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = None
    password: str = Field(..., min_length=6)
    display_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== DataSource =====
class DataSourceCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    source_type: str
    connection_mode: str = "direct"
    config: dict


class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class DataSourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    source_type: str
    connection_mode: str
    config: Optional[Any] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== Dataset =====
class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    dataset_type: str = "table"
    datasource_id: Optional[int] = None
    source_table: Optional[str] = None
    sql_query: Optional[str] = None
    fields_config: Optional[list] = None
    transformations: Optional[dict] = None
    sync_config: Optional[dict] = None


class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields_config: Optional[list] = None
    transformations: Optional[dict] = None
    sync_config: Optional[dict] = None


class DatasetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    dataset_type: str
    datasource_id: Optional[int] = None
    source_table: Optional[str] = None
    sql_query: Optional[str] = None
    fields_config: Optional[Any] = None
    transformations: Optional[Any] = None
    sync_config: Optional[Any] = None
    data_sample: Optional[Any] = None
    row_count: int = 0
    is_synced: bool = False
    last_sync_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== Chart =====
class ChartCreate(BaseModel):
    name: Optional[str] = ""
    chart_type: str
    dataset_id: int
    dimensions: list = []
    measures: list = []
    config: dict = {}
    color_schema: list = []
    sort_config: dict = {}
    filter_config: list = []
    drill_down: dict = {}


class ChartResponse(BaseModel):
    id: int
    name: Optional[str] = None
    chart_type: str
    dataset_id: int
    dimensions: Optional[Any] = None
    measures: Optional[Any] = None
    config: Optional[Any] = None
    color_schema: Optional[Any] = None
    sort_config: Optional[Any] = None
    filter_config: Optional[Any] = None
    drill_down: Optional[Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== Dashboard =====
class DashboardCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    dashboard_type: str = "dashboard"
    layout: dict = {}
    background_config: dict = {}
    style_config: dict = {}
    width: int = 1920
    height: int = 1080


class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    layout: Optional[dict] = None
    background_config: Optional[dict] = None
    style_config: Optional[dict] = None
    filter_config: Optional[list] = None
    is_published: Optional[bool] = None


class DashboardResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    dashboard_type: str
    layout: Optional[Any] = None
    background_config: Optional[Any] = None
    style_config: Optional[Any] = None
    filter_config: Optional[Any] = None
    width: int
    height: int
    is_published: bool
    thumbnail: Optional[str] = None
    share_token: Optional[str] = None
    embed_token: Optional[str] = None
    visit_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DashboardViewCreate(BaseModel):
    dashboard_id: int
    title: Optional[str] = ""
    chart_id: Optional[int] = None
    position: dict = {}
    style: dict = {}
    interactions: dict = {}


class DashboardViewUpdate(BaseModel):
    title: Optional[str] = None
    position: Optional[dict] = None
    style: Optional[dict] = None
    interactions: Optional[dict] = None
    chart_id: Optional[int] = None


class DashboardViewResponse(BaseModel):
    id: int
    dashboard_id: int
    title: Optional[str] = None
    chart_id: Optional[int] = None
    position: Optional[Any] = None
    style: Optional[Any] = None
    interactions: Optional[Any] = None
    chart: Optional[ChartResponse] = None

    class Config:
        from_attributes = True


# ===== Dashboard Share =====
class ShareCreate(BaseModel):
    password: Optional[str] = None
    expire_days: Optional[int] = None


# ===== General =====
class QueryRequest(BaseModel):
    dataset_id: int
    dimensions: list = []
    measures: list = []
    filters: list = []
    sort: list = []
    limit: int = 1000
    offset: int = 0


class MessageResponse(BaseModel):
    message: str
    status: str = "ok"


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int = 1
    page_size: int = 20
