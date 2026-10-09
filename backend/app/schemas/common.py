"""
Common Schemas

This module contains common Pydantic schemas used across the application.
"""

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar('T')


class MessageResponse(BaseModel):
    """
    Standard message response schema.
    """
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Whether the operation was successful")
    details: Optional[str] = Field(default=None, description="Additional details")


class ErrorResponse(BaseModel):
    """
    Error response schema.
    """
    message: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[str] = Field(default=None, description="Error details")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response schema.
    """
    items: List[T] = Field(default_factory=list, description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")


class QueryParams(BaseModel):
    """
    Standard query parameters for pagination and filtering.
    """
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=10, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(default=None, description="Search term")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: Optional[str] = Field(default="desc", description="Sort order (asc or desc)")
    
    class Config:
        populate_by_name = True


class HealthResponse(BaseModel):
    """
    Health check response schema.
    """
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Current timestamp")
    checks: Optional[dict] = Field(default=None, description="Health check details")