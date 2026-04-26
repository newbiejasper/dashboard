# -*- coding: utf-8 -*-
"""DDYL DataSource Model - 多源数据源连接"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class DataSource(Base):
    """数据源 - 支持20+种数据源连接"""
    __tablename__ = "datasources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    source_type = Column(String(50), nullable=False)  # mysql, clickhouse, starrocks, excel, csv, api, kafka, redis
    connection_mode = Column(String(20), default="direct")  # direct, local_cache
    config = Column(JSON, nullable=False)  # connection config (host, port, user, password, database, etc.)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="datasources")
    datasets = relationship("Dataset", back_populates="datasource", cascade="all, delete-orphan")


class Dataset(Base):
    """数据集 - 数据准备与处理"""
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    dataset_type = Column(String(30), nullable=False)  # table, sql, file, cross_source, api
    source_table = Column(String(200))  # original table name
    sql_query = Column(Text)  # custom SQL
    fields_config = Column(JSON)  # field definitions, type mappings
    transformations = Column(JSON)  # transformation pipeline (filter, sort, aggregate, join)
    sync_config = Column(JSON)  # sync schedule config
    data_sample = Column(JSON)  # sample data preview
    row_count = Column(Integer, default=0)
    is_synced = Column(Boolean, default=False)
    last_sync_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    datasource_id = Column(Integer, ForeignKey("datasources.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="datasets")
    datasource = relationship("DataSource", back_populates="datasets")
    charts = relationship("Chart", back_populates="dataset", cascade="all, delete-orphan")


class DatasetCache(Base):
    """数据集缓存 - Doris高速缓存"""
    __tablename__ = "dataset_caches"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    cache_key = Column(String(200), index=True)
    cache_data = Column(JSON)
    cache_sql = Column(Text)
    query_time_ms = Column(Integer)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
