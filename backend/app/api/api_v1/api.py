# -*- coding: utf-8 -*-
"""DDYL API v1 Router"""
from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, datasources, datasets, dashboards

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(datasources.router)
api_router.include_router(datasets.router)
api_router.include_router(dashboards.router)
