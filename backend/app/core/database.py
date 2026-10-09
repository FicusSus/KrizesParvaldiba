"""
Database Configuration and Connection Management

This module provides async database connections using SQLAlchemy and asyncpg.
It supports connection pooling for handling large datasets efficiently.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Database engine
engine: Optional[AsyncSession] = None
async_session_maker: Optional[async_sessionmaker] = None


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    """
    pass


def create_engine():
    """
    Create async database engine with connection pooling.
    
    Returns:
        AsyncEngine: SQLAlchemy async engine.
    """
    logger.info("Creating database engine", url=settings.DATABASE_URL)
    
    return create_async_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


def create_session_maker(engine) -> async_sessionmaker:
    """
    Create async session maker.
    
    Args:
        engine: SQLAlchemy async engine.
        
    Returns:
        async_sessionmaker: Session factory.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def init_db():
    """
    Initialize database connections.
    """
    global engine, async_session_maker
    
    if engine is None:
        engine = create_engine()
        async_session_maker = create_session_maker(engine)
        logger.info("Database connections initialized")


async def close_db():
    """
    Close database connections.
    """
    global engine, async_session_maker
    
    if engine is not None:
        await engine.dispose()
        engine = None
        async_session_maker = None
        logger.info("Database connections closed")


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session with async context manager.
    
    Yields:
        AsyncSession: Database session.
    """
    if async_session_maker is None:
        await init_db()
    
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error("Database transaction failed", error=str(e))
        raise
    finally:
        await session.close()


async def get_session() -> AsyncSession:
    """
    Get database session (for dependency injection).
    
    Returns:
        AsyncSession: Database session.
    """
    async with get_db() as session:
        yield session


# For FastAPI dependency injection
async def get_async_session() -> AsyncSession:
    """
    FastAPI dependency for database sessions.
    
    Returns:
        AsyncSession: Database session.
    """
    async for session in get_session():
        yield session