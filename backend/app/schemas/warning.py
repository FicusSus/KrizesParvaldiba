"""
Warning Schemas

This module contains Pydantic schemas for Warning operations.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.warning import WarningPriority, WarningStatus, WarningType
from app.schemas.common import MessageResponse


class WarningBase(BaseModel):
    """
    Base warning schema with common fields.
    """
    subject: str = Field(..., max_length=200, description="Warning subject/title")
    message: str = Field(..., description="Warning message content")


class WarningCreate(WarningBase):
    """
    Schema for creating a new warning.
    """
    user_id: Optional[int] = Field(default=None, description="Reference to user")
    crisis_id: Optional[int] = Field(default=None, description="Reference to crisis")
    warning_type: WarningType = Field(default=WarningType.EMAIL, description="Type of warning")
    priority: WarningPriority = Field(default=WarningPriority.MEDIUM, description="Priority level")
    recipient: Optional[str] = Field(default=None, max_length=255, description="Recipient address")
    metadata: Optional[dict] = Field(default={}, description="Additional metadata")


class WarningUpdate(BaseModel):
    """
    Schema for updating a warning.
    """
    user_id: Optional[int] = Field(default=None, description="Reference to user")
    crisis_id: Optional[int] = Field(default=None, description="Reference to crisis")
    warning_type: Optional[WarningType] = Field(default=None, description="Type of warning")
    priority: Optional[WarningPriority] = Field(default=None, description="Priority level")
    status: Optional[WarningStatus] = Field(default=None, description="Current status")
    subject: Optional[str] = Field(default=None, max_length=200, description="Warning subject/title")
    message: Optional[str] = Field(default=None, description="Warning message content")
    recipient: Optional[str] = Field(default=None, max_length=255, description="Recipient address")
    is_read: Optional[bool] = Field(default=None, description="Whether warning has been read")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


class WarningResponse(WarningBase):
    """
    Schema for warning response.
    """
    id: int = Field(..., description="Warning ID")
    user_id: Optional[int] = Field(default=None, description="Reference to user")
    crisis_id: Optional[int] = Field(default=None, description="Reference to crisis")
    warning_type: WarningType = Field(..., description="Type of warning")
    priority: WarningPriority = Field(..., description="Priority level")
    status: WarningStatus = Field(..., description="Current status")
    recipient: Optional[str] = Field(default=None, max_length=255, description="Recipient address")
    is_read: bool = Field(default=False, description="Whether warning has been read")
    send_attempts: int = Field(default=0, description="Number of send attempts")
    last_attempt: Optional[datetime] = Field(default=None, description="Last send attempt timestamp")
    error_message: Optional[str] = Field(default=None, description="Error message")
    metadata: dict = Field(default={}, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_sent: bool = Field(..., description="Whether warning has been sent")
    is_delivered: bool = Field(..., description="Whether warning has been delivered")
    should_retry: bool = Field(..., description="Whether warning should be retried")
    
    class Config:
        from_attributes = True