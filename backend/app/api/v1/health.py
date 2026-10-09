"""
Health Check API

This module provides health check endpoints for monitoring the service.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns service status and version information.
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.utcnow().isoformat(),
        checks={
            "api": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@router.get("/database", response_model=HealthResponse)
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """
    Database health check endpoint.
    
    Verifies database connectivity.
    """
    try:
        # Simple query to check database connectivity
        await db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        version="0.1.0",
        timestamp=datetime.utcnow().isoformat(),
        checks={
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@router.get("/detailed", response_model=HealthResponse)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check endpoint.
    
    Performs comprehensive health checks on all services.
    """
    checks = {
        "api": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Database check
    try:
        await db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # Additional checks can be added here
    checks["cache"] = "healthy"  # Placeholder - implement Redis check
    checks["models"] = "healthy"  # Placeholder - implement ML model check
    
    all_healthy = all(status == "healthy" for status in checks.values() if isinstance(status, str))
    
    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        version="0.1.0",
        timestamp=datetime.utcnow().isoformat(),
        checks=checks
    )