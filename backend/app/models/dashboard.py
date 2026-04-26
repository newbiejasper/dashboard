# -*- coding: utf-8 -*-
"""DDYL Dashboard Model - 仪表板与大屏"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Dashboard(Base):
    """仪表板/大屏"""
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    dashboard_type = Column(String(20), default="dashboard")  # dashboard, screen (大屏)
    layout = Column(JSON, default=dict)  # grid layout config
    background_config = Column(JSON, default=dict)  # bg color, image, opacity
    style_config = Column(JSON, default=dict)  # fonts, colors, theme
    filter_config = Column(JSON, default=list)  # global filter components
    width = Column(Integer, default=1920)
    height = Column(Integer, default=1080)
    is_published = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    template_category = Column(String(100))
    thumbnail = Column(String(500))
    share_token = Column(String(64), unique=True)
    share_password = Column(String(100))
    embed_token = Column(String(64), unique=True)
    visit_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="dashboards")
    views = relationship("DashboardView", back_populates="dashboard", cascade="all, delete-orphan")
    filters = relationship("DashboardFilter", back_populates="dashboard", cascade="all, delete-orphan")


class DashboardView(Base):
    """仪表板中的视图/图表"""
    __tablename__ = "dashboard_views"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    title = Column(String(200))
    chart_id = Column(Integer, ForeignKey("charts.id"), nullable=True)
    position = Column(JSON, default=dict)  # x, y, w, h in grid
    style = Column(JSON, default=dict)  # custom style overrides
    interactions = Column(JSON, default=dict)  # linkage, drill-down, jump config
    created_at = Column(DateTime, default=datetime.utcnow)

    dashboard = relationship("Dashboard", back_populates="views")
    chart = relationship("Chart")


class DashboardFilter(Base):
    """仪表板全局过滤组件"""
    __tablename__ = "dashboard_filters"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    filter_type = Column(String(30))  # dropdown, date_picker, text_input, slider
    field_name = Column(String(200))
    title = Column(String(100))
    position = Column(JSON, default=dict)
    config = Column(JSON, default=dict)  # options, default value, etc.
    linked_views = Column(JSON, default=list)  # which views this filter affects

    dashboard = relationship("Dashboard", back_populates="filters")


class Chart(Base):
    """图表定义 - 30+种图表类型"""
    __tablename__ = "charts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    chart_type = Column(String(50), nullable=False)  # bar, line, pie, funnel, sankey, heatmap, etc.
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    dimensions = Column(JSON, default=list)  # dimension fields
    measures = Column(JSON, default=list)    # measure fields
    config = Column(JSON, default=dict)      # ECharts config options
    color_schema = Column(JSON, default=list)
    sort_config = Column(JSON, default=dict)
    filter_config = Column(JSON, default=list)
    drill_down = Column(JSON, default=dict)  # drill-down hierarchy
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    dataset = relationship("Dataset", back_populates="charts")
