# -*- coding: utf-8 -*-
"""DDYL Dashboard API - 仪表板管理"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.dashboard import Dashboard, DashboardView, DashboardFilter, Chart
from app.models.datasource import Dataset
from app.schemas import (
    DashboardCreate, DashboardUpdate, DashboardResponse,
    DashboardViewCreate, DashboardViewUpdate, DashboardViewResponse,
    ChartCreate, ChartResponse,
    ShareCreate, MessageResponse, PaginatedResponse,
)

router = APIRouter(prefix="/dashboards", tags=["仪表板管理"])


# ===== Dashboard CRUD =====

@router.get("/", response_model=list[DashboardResponse])
async def list_dashboards(
    dashboard_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取仪表板列表"""
    query = select(Dashboard).where(Dashboard.owner_id == current_user.id)
    if dashboard_type:
        query = query.where(Dashboard.dashboard_type == dashboard_type)
    query = query.order_by(Dashboard.updated_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/recent", response_model=list[DashboardResponse])
async def recent_dashboards(
    limit: int = Query(10, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """最近访问的仪表板"""
    query = (
        select(Dashboard)
        .where(Dashboard.owner_id == current_user.id, Dashboard.dashboard_type == "dashboard")
        .order_by(Dashboard.updated_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stats")
async def dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """工作台统计概览"""
    dash_count = await db.execute(
        select(func.count(Dashboard.id)).where(
            Dashboard.owner_id == current_user.id,
            Dashboard.dashboard_type == "dashboard",
        )
    )
    screen_count = await db.execute(
        select(func.count(Dashboard.id)).where(
            Dashboard.owner_id == current_user.id,
            Dashboard.dashboard_type == "screen",
        )
    )
    from app.models.datasource import DataSource, Dataset
    ds_count = await db.execute(
        select(func.count(DataSource.id)).where(DataSource.owner_id == current_user.id)
    )
    dt_count = await db.execute(
        select(func.count(Dataset.id)).where(Dataset.owner_id == current_user.id)
    )

    return {
        "dashboard_count": dash_count.scalar() or 0,
        "screen_count": screen_count.scalar() or 0,
        "datasource_count": ds_count.scalar() or 0,
        "dataset_count": dt_count.scalar() or 0,
    }


@router.post("/", response_model=DashboardResponse)
async def create_dashboard(
    db_in: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建仪表板"""
    dashboard = Dashboard(
        name=db_in.name,
        description=db_in.description or "",
        dashboard_type=db_in.dashboard_type,
        layout=db_in.layout or {},
        background_config=db_in.background_config or {},
        style_config=db_in.style_config or {},
        width=db_in.width,
        height=db_in.height,
        share_token=secrets.token_urlsafe(32),
        embed_token=secrets.token_urlsafe(32),
        owner_id=current_user.id,
    )
    db.add(dashboard)
    await db.flush()
    await db.refresh(dashboard)
    return dashboard


@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取仪表板详情"""
    result = await db.execute(
        select(Dashboard).where(Dashboard.id == dashboard_id)
    )
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    dashboard.visit_count = (dashboard.visit_count or 0) + 1
    await db.flush()
    return dashboard


@router.put("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: int,
    db_in: DashboardUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新仪表板"""
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.owner_id == current_user.id,
        )
    )
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    for field, value in db_in.dict(exclude_unset=True).items():
        setattr(dashboard, field, value)
    await db.flush()
    await db.refresh(dashboard)
    return dashboard


@router.delete("/{dashboard_id}", response_model=MessageResponse)
async def delete_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除仪表板"""
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.owner_id == current_user.id,
        )
    )
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    await db.delete(dashboard)
    return MessageResponse(message="Dashboard deleted")


# ===== Dashboard Views (Charts in Dashboard) =====

@router.get("/{dashboard_id}/views", response_model=list[DashboardViewResponse])
async def list_views(
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取仪表板中的视图列表"""
    result = await db.execute(
        select(DashboardView)
        .where(DashboardView.dashboard_id == dashboard_id)
        .order_by(DashboardView.id)
    )
    views = result.scalars().all()
    # Eager load chart data
    result_list = []
    for view in views:
        view_data = {
            "id": view.id,
            "dashboard_id": view.dashboard_id,
            "title": view.title,
            "chart_id": view.chart_id,
            "position": view.position,
            "style": view.style,
            "interactions": view.interactions,
            "chart": None,
        }
        if view.chart_id:
            chart_result = await db.execute(
                select(Chart).where(Chart.id == view.chart_id)
            )
            chart = chart_result.scalar_one_or_none()
            if chart:
                view_data["chart"] = chart
        result_list.append(view_data)
    return result_list


@router.post("/{dashboard_id}/views", response_model=DashboardViewResponse)
async def add_view(
    dashboard_id: int,
    view_in: DashboardViewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加视图到仪表板"""
    view = DashboardView(
        dashboard_id=dashboard_id,
        title=view_in.title or "",
        chart_id=view_in.chart_id,
        position=view_in.position or {},
        style=view_in.style or {},
        interactions=view_in.interactions or {},
    )
    db.add(view)
    await db.flush()
    await db.refresh(view)

    chart = None
    if view.chart_id:
        chart_result = await db.execute(select(Chart).where(Chart.id == view.chart_id))
        chart = chart_result.scalar_one_or_none()

    return {
        "id": view.id,
        "dashboard_id": view.dashboard_id,
        "title": view.title,
        "chart_id": view.chart_id,
        "position": view.position,
        "style": view.style,
        "interactions": view.interactions,
        "chart": chart,
    }


@router.put("/{dashboard_id}/views/{view_id}", response_model=DashboardViewResponse)
async def update_view(
    dashboard_id: int,
    view_id: int,
    view_in: DashboardViewUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新视图"""
    result = await db.execute(
        select(DashboardView).where(
            DashboardView.id == view_id,
            DashboardView.dashboard_id == dashboard_id,
        )
    )
    view = result.scalar_one_or_none()
    if not view:
        raise HTTPException(status_code=404, detail="View not found")
    for field, value in view_in.dict(exclude_unset=True).items():
        setattr(view, field, value)
    await db.flush()
    await db.refresh(view)

    chart = None
    if view.chart_id:
        chart_result = await db.execute(select(Chart).where(Chart.id == view.chart_id))
        chart = chart_result.scalar_one_or_none()

    return {
        "id": view.id,
        "dashboard_id": view.dashboard_id,
        "title": view.title,
        "chart_id": view.chart_id,
        "position": view.position,
        "style": view.style,
        "interactions": view.interactions,
        "chart": chart,
    }


@router.delete("/{dashboard_id}/views/{view_id}", response_model=MessageResponse)
async def remove_view(
    dashboard_id: int,
    view_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除视图"""
    result = await db.execute(
        select(DashboardView).where(
            DashboardView.id == view_id,
            DashboardView.dashboard_id == dashboard_id,
        )
    )
    view = result.scalar_one_or_none()
    if not view:
        raise HTTPException(status_code=404, detail="View not found")
    await db.delete(view)
    return MessageResponse(message="View deleted")


# ===== Charts =====

@router.post("/charts", response_model=ChartResponse)
async def create_chart(
    chart_in: ChartCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建图表"""
    chart = Chart(
        name=chart_in.name or chart_in.chart_type,
        chart_type=chart_in.chart_type,
        dataset_id=chart_in.dataset_id,
        dimensions=chart_in.dimensions or [],
        measures=chart_in.measures or [],
        config=chart_in.config or {},
        color_schema=chart_in.color_schema or [],
        sort_config=chart_in.sort_config or {},
        filter_config=chart_in.filter_config or [],
        drill_down=chart_in.drill_down or {},
        owner_id=current_user.id,
    )
    db.add(chart)
    await db.flush()
    await db.refresh(chart)
    return chart


@router.get("/charts/{chart_id}", response_model=ChartResponse)
async def get_chart(
    chart_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取图表详情"""
    result = await db.execute(
        select(Chart).where(Chart.id == chart_id)
    )
    chart = result.scalar_one_or_none()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    return chart


@router.put("/charts/{chart_id}", response_model=ChartResponse)
async def update_chart(
    chart_id: int,
    chart_in: ChartCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新图表"""
    result = await db.execute(
        select(Chart).where(Chart.id == chart_id)
    )
    chart = result.scalar_one_or_none()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    for field, value in chart_in.dict(exclude_unset=True).items():
        setattr(chart, field, value)
    await db.flush()
    await db.refresh(chart)
    return chart


@router.delete("/charts/{chart_id}", response_model=MessageResponse)
async def delete_chart(
    chart_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除图表"""
    result = await db.execute(select(Chart).where(Chart.id == chart_id))
    chart = result.scalar_one_or_none()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    await db.delete(chart)
    return MessageResponse(message="Chart deleted")


# ===== Share & Embed =====

@router.post("/{dashboard_id}/share")
async def share_dashboard(
    dashboard_id: int,
    share_in: ShareCreate = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """生成分享链接"""
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.owner_id == current_user.id,
        )
    )
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    if share_in and share_in.password:
        dashboard.share_password = share_in.password
        await db.flush()
    return {
        "share_url": f"/share/{dashboard.share_token}",
        "embed_url": f"/embed/{dashboard.embed_token}",
        "share_token": dashboard.share_token,
        "embed_token": dashboard.embed_token,
        "has_password": bool(dashboard.share_password),
    }


# ===== Templates =====

@router.get("/templates", response_model=list[DashboardResponse])
async def list_templates(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取模板列表"""
    query = select(Dashboard).where(Dashboard.is_template == True)
    if category:
        query = query.where(Dashboard.template_category == category)
    query = query.order_by(Dashboard.visit_count.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/templates/{template_id}/use", response_model=DashboardResponse)
async def use_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """使用模板创建仪表板"""
    result = await db.execute(select(Dashboard).where(Dashboard.id == template_id))
    template = result.scalar_one_or_none()
    if not template or not template.is_template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Clone template
    new_dashboard = Dashboard(
        name=f"{template.name} (副本)",
        description=template.description,
        dashboard_type=template.dashboard_type,
        layout=template.layout,
        background_config=template.background_config,
        style_config=template.style_config,
        filter_config=[],
        width=template.width,
        height=template.height,
        share_token=secrets.token_urlsafe(32),
        embed_token=secrets.token_urlsafe(32),
        owner_id=current_user.id,
    )
    db.add(new_dashboard)
    await db.flush()
    await db.refresh(new_dashboard)

    # Clone views from template
    views_result = await db.execute(
        select(DashboardView).where(DashboardView.dashboard_id == template_id)
    )
    for view in views_result.scalars().all():
        new_view = DashboardView(
            dashboard_id=new_dashboard.id,
            title=view.title,
            chart_id=view.chart_id,
            position=view.position,
            style=view.style,
            interactions=view.interactions,
        )
        db.add(new_view)

    await db.flush()
    await db.refresh(new_dashboard)
    return new_dashboard
