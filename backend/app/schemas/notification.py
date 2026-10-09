"""
Notification Schema

This module contains Pydantic schemas for user notifications.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.schemas.common import MessageResponse


class NotificationBase(BaseModel):
    """Base notification schema with common fields."""
    
    user_id: Optional[int] = Field(
        default=None,
        description="Reference to the user receiving the notification"
    )
    notification_type: str = Field(
        ...,
        max_length=20,
        description="Type of notification (info, warning, error, success)"
    )
    channel: str = Field(
        ...,
        max_length=20,
        description="Delivery channel (email, sms, push, webhook, in_app)"
    )
    title: str = Field(
        ...,
        max_length=200,
        description="Notification title"
    )
    message: str = Field(
        ...,
        description="Notification message content"
    )


class NotificationCreate(NotificationBase):
    """Schema for creating a new notification."""
    
    is_read: bool = Field(
        default=False,
        description="Whether the notification has been read"
    )
    is_archived: bool = Field(
        default=False,
        description="Whether the notification has been archived"
    )
    extra_data: Optional[Dict[str, Any]] = Field(
        default={},
        description="Additional notification metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "notification_type": "info",
                "channel": "in_app",
                "title": "System Update",
                "message": "The system has been updated to version 1.0.0",
                "is_read": False,
                "is_archived": False,
                "extra_data": {}
            }
        }


class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""
    
    user_id: Optional[int] = Field(
        default=None,
        description="Reference to the user"
    )
    notification_type: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Type of notification"
    )
    channel: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Delivery channel"
    )
    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Notification title"
    )
    message: Optional[str] = Field(
        default=None,
        description="Notification message"
    )
    is_read: Optional[bool] = Field(
        default=None,
        description="Whether the notification has been read"
    )
    is_archived: Optional[bool] = Field(
        default=None,
        description="Whether the notification has been archived"
    )
    extra_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional notification metadata"
    )


class NotificationResponse(NotificationBase):
    """Schema for notification response with all fields."""
    
    id: int = Field(
        ...,
        description="Unique identifier for the notification"
    )
    is_read: bool = Field(
        ...,
        description="Whether the notification has been read"
    )
    is_archived: bool = Field(
        ...,
        description="Whether the notification has been archived"
    )
    extra_data: Dict[str, Any] = Field(
        default={},
        description="Additional notification metadata"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when notification was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when notification was last updated"
    )
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "notification_type": "info",
                "channel": "in_app",
                "title": "System Update",
                "message": "The system has been updated to version 1.0.0",
                "is_read": False,
                "is_archived": False,
                "extra_data": {},
                "created_at": "2026-10-09T10:00:00Z",
                "updated_at": "2026-10-09T10:00:00Z"
            }
        }
