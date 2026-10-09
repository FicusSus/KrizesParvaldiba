"""
API v1 Module

This module contains all v1 API routers and endpoints.
"""

from app.api.v1.health import router as health_router
from app.api.v1.users import router as users_router
from app.api.v1.data import router as data_router
from app.api.v1.crisis import router as crisis_router
from app.api.v1.warnings import router as warnings_router

__all__ = ["health_router", "users_router", "data_router", "crisis_router", "warnings_router"]