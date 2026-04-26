# -*- coding: utf-8 -*-
"""DDYL Configuration Module"""
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "DDYL BI Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ddyl.db"
    DATABASE_ECHO: bool = False

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "ddyl-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # File Upload
    UPLOAD_DIR: str = "media/uploads"
    MAX_FILE_SIZE: int = 104857600
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls", ".txt", ".json", ".xml"]

    # Doris Engine
    DORIS_HOST: str = "localhost"
    DORIS_PORT: int = 9030
    DORIS_USER: str = "root"
    DORIS_PASSWORD: str = ""

    # Templates
    TEMPLATE_DIR: str = "media/templates"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
