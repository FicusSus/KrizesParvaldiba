"""
Main FastAPI Application

This is the entry point for the Crisis Prediction Backend API.
It initializes the FastAPI app, includes all routers, and sets up middleware.
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routers
from app.api.v1 import crisis, data, health, users, warnings
from app.core import config, database
from app.core.logger import setup_logging

# Configure logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Crisis Prediction Backend API")
    
    # Initialize database connections
    await database.init_db()
    logger.info("Database connections initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Crisis Prediction Backend API")
    await database.close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="Crisis Prediction API",
    description="""
    # Crisis Prediction and Warning System API
    
    This API provides:
    - **Data Ingestion**: Process large datasets for crisis analysis
    - **Prediction Engine**: ML models for crisis prediction
    - **Warning System**: Real-time alerts and notifications
    - **User Management**: Authentication and user preferences
    
    ## Features
    
    * High-performance data processing with Polars and Pandas
    * Async database operations
    * Machine learning integration
    * Real-time warnings via WebSocket/Email/SMS
    * Scalable architecture for large datasets
    """,
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(data.router, prefix="/api/v1/data", tags=["data"])
app.include_router(crisis.router, prefix="/api/v1/crisis", tags=["crisis"])
app.include_router(warnings.router, prefix="/api/v1/warnings", tags=["warnings"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error("Unhandled exception", exc_info=exc, request_url=str(request.url))
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc) if config.settings.DEBUG else None,
        },
    )


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint returning API information.
    """
    return {
        "name": "Crisis Prediction API",
        "version": "0.1.0",
        "description": "Backend API for Crisis Prediction and Warning System",
        "docs": "/api/docs",
    }


# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=config.settings.HOST,
        port=config.settings.PORT,
        reload=config.settings.DEBUG,
        log_level="debug" if config.settings.DEBUG else "info",
    )