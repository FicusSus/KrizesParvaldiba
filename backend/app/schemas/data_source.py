"""
Data Source Schemas

This module contains Pydantic schemas for Data Source operations.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.data_source import DataSourceType
from app.schemas.common import MessageResponse


class DataSourceBase(BaseModel):
    """
    Base data source schema with common fields.
    """
    name: str = Field(..., max_length=100, description="Data source name")
    source_type: DataSourceType = Field(..., description="Type of data source")
    connection_string: str = Field(..., description="Connection string or URL")
    description: Optional[str] = Field(default=None, description="Description of the data source")


class DataSourceCreate(DataSourceBase):
    """
    Schema for creating a new data source.
    """
    config: Optional[dict] = Field(default={}, description="Configuration as JSON")
    is_active: bool = Field(default=True, description="Whether the data source is active")


class DataSourceUpdate(BaseModel):
    """
    Schema for updating a data source.
    """
    name: Optional[str] = Field(default=None, max_length=100, description="Data source name")
    source_type: Optional[DataSourceType] = Field(default=None, description="Type of data source")
    connection_string: Optional[str] = Field(default=None, description="Connection string or URL")
    description: Optional[str] = Field(default=None, description="Description of the data source")
    config: Optional[dict] = Field(default=None, description="Configuration as JSON")
    is_active: Optional[bool] = Field(default=None, description="Whether the data source is active")


class DataSourceResponse(DataSourceBase):
    """
    Schema for data source response.
    """
    id: int = Field(..., description="Data source ID")
    config: dict = Field(default={}, description="Configuration as JSON")
    is_active: bool = Field(..., description="Whether the data source is active")
    last_sync: Optional[datetime] = Field(default=None, description="Last synchronization timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_available: bool = Field(..., description="Whether data source is available")
    
    class Config:
        from_attributes = True