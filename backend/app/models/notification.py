"""
Notification Model

This module contains models for user notifications.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class NotificationType(str, enum.Enum):
    """Types of notifications."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class NotificationChannel(str, enum.Enum):
    """Channels for notifications."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class Notification(Base):
    """
    Notification model representing user notifications.
    
    Attributes:
        id: Unique identifier
        user_id: Reference to the user receiving the notification
        notification_type: Type of notification
        channel: Delivery channel
        title: Notification title
        message: Notification message
        is_read: Whether the notification has been read
        is_archived: Whether the notification has been archived
        metadata: Additional metadata as JSON
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType),
        default=NotificationType.INFO,
        nullable=False
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel),
        default=NotificationChannel.IN_APP,
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata: Mapped[Optional[dict]] = mapped_column(Text, default={})
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="notifications"
    )
    
    def __repr__(self) -> str:
        return f"Notification(id={self.id}, type={self.notification_type}, title={self.title})"
    
    @property
    def is_unread(self) -> bool:
        """Check if notification is unread."""
        return not self.is_read