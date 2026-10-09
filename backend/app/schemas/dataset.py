"""
Dataset Schemas

This module contains Pydantic schemas for Dataset operations.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.dataset import DatasetStatus, DatasetType
from app.schemas.common import MessageResponse


class DatasetBase(BaseModel):
    """
    Base dataset schema with common fields.
    """
    name: str = Field(..., max_length=200, description="Dataset name")
    file_path: str = Field(..., description="Path to the data file")


class DatasetCreate(DatasetBase):
    """
    Schema for creating a new dataset.
    """
    data_source_id: Optional[int] = Field(default=None, description="Reference to data source")
    dataset_type: DatasetType = Field(default=DatasetType.RAW, description="Type of dataset")
    status: DatasetStatus = Field(default=DatasetStatus.PENDING, description="Processing status")
    metadata: Optional[dict] = Field(default={}, description="Additional metadata as JSON")


class DatasetUpdate(BaseModel):
    """
    Schema for updating a dataset.
    """
    name: Optional[str] = Field(default=None, max_length=200, description="Dataset name")
    file_path: Optional[str] = Field(default=None, description="Path to the data file")
    data_source_id: Optional[int] = Field(default=None, description="Reference to data source")
    dataset_type: Optional[DatasetType] = Field(default=None, description="Type of dataset")
    status: Optional[DatasetStatus] = Field(default=None, description="Processing status")
    row_count: Optional[int] = Field(default=None, description="Number of rows")
    column_count: Optional[int] = Field(default=None, description="Number of columns")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata as JSON")
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")
    error_message: Optional[str] = Field(default=None, description="Error message")


class DatasetResponse(DatasetBase):
    """
    Schema for dataset response.
    """
    id: int = Field(..., description="Dataset ID")
    data_source_id: Optional[int] = Field(default=None, description="Reference to data source")
    dataset_type: DatasetType = Field(..., description="Type of dataset")
    status: DatasetStatus = Field(..., description="Processing status")
    row_count: Optional[int] = Field(default=None, description="Number of rows")
    column_count: Optional[int] = Field(default=None, description="Number of columns")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    metadata: dict = Field(default={}, description="Additional metadata as JSON")
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")
    error_message: Optional[str] = Field(default=None, description="Error message")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_processed: bool = Field(..., description="Whether dataset has been processed")
    is_processing: bool = Field(..., description="Whether dataset is currently processing")
    
    class Config:
        from_attributes = True