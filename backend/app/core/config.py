"""
Configuration Management

This module handles all application configuration using Pydantic Settings.
Environment variables are loaded from .env files or system environment.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Application
    APP_NAME: str = "Crisis Prediction Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/crisis_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False
    
    # Redis (for caching and queue)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Data Processing
    DATA_DIR: Path = Path("data")
    RAW_DATA_DIR: Path = Path("data/raw")
    PROCESSED_DATA_DIR: Path = Path("data/processed")
    MODELS_DIR: Path = Path("data/models")
    CHUNK_SIZE: int = 10000  # For processing large datasets
    MAX_MEMORY_USAGE: float = 0.8  # 80% of available memory
    
    # ML Models
    MODEL_SAVE_PATH: Path = Path("ml/models")
    FEATURES_DIR: Path = Path("ml/features")
    
    # Notifications
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "user@example.com"
    SMTP_PASSWORD: str = "password"
    SMTP_FROM: str = "no-reply@example.com"
    
    # Twilio for SMS (optional)
    TWILIO_SID: Optional[str] = None
    TWILIO_TOKEN: Optional[str] = None
    TWILIO_PHONE: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: Path = Path("logs/app.log")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.DEBUG
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.DEBUG


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: The application settings.
    """
    return Settings()


# Global settings instance
settings = get_settings()