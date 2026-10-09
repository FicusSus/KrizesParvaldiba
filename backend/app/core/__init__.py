"""
Core module for the Crisis Prediction Backend.

Contains configuration, database, security, and other core functionalities.
"""

from app.core.config import settings
from app.core.database import get_db, init_db, close_db

__all__ = ["settings", "get_db", "init_db", "close_db"]