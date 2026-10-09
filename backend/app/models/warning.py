"""
Warning Model

This module contains models for user warnings and alerts.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.crisis import Crisis


class WarningType(str, enum.Enum):
    """Types of warnings."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class WarningStatus(str, enum.Enum):
    """Status of warnings."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class WarningPriority(str, enum.Enum):
    """Priority levels for warnings."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Warning(Base):
    """
    Warning model representing user alerts and notifications.
    
    Attributes:
        id: Unique identifier
        user_id: Reference to the user receiving the warning
        crisis_id: Reference to the crisis triggering the warning
        warning_type: Type of warning (email, SMS, etc.)
        priority: Priority level
        status: Current status
        subject: Warning subject/title
        message: Warning message content
        recipient: Recipient address (email, phone, etc.)
        is_read: Whether the warning has been read
        send_attempts: Number of send attempts
        last_attempt: Last send attempt timestamp
        error_message: Error message if sending failed
        extra_data: Additional metadata as JSON
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "warnings"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    crisis_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("crisis_events.id", ondelete="SET NULL")
    )
    warning_type: Mapped[WarningType] = mapped_column(
        Enum(WarningType),
        default=WarningType.EMAIL,
        nullable=False
    )
    priority: Mapped[WarningPriority] = mapped_column(
        Enum(WarningPriority),
        default=WarningPriority.MEDIUM,
        nullable=False
    )
    status: Mapped[WarningStatus] = mapped_column(
        Enum(WarningStatus),
        default=WarningStatus.PENDING,
        nullable=False
    )
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    recipient: Mapped[Optional[str]] = mapped_column(String(255))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    send_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_attempt: Mapped[Optional[datetime]] = mapped_column(DateTime)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    extra_data: Mapped[Optional[dict]] = mapped_column(Text, default={})
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
        back_populates="warnings"
    )
    crisis: Mapped[Optional["Crisis"]] = relationship(
        "Crisis",
        back_populates="warnings"
    )
    
    def __repr__(self) -> str:
        return f"Warning(id={self.id}, type={self.warning_type}, priority={self.priority}, subject={self.subject})"
    
    @property
    def is_sent(self) -> bool:
        """Check if warning has been sent."""
        return self.status in [WarningStatus.SENT, WarningStatus.DELIVERED, WarningStatus.READ]
    
    @property
    def is_delivered(self) -> bool:
        """Check if warning has been delivered."""
        return self.status in [WarningStatus.DELIVERED, WarningStatus.READ]
    
    @property
    def should_retry(self) -> bool:
        """Check if warning should be retried (failed but not too many attempts)."""
        return (self.status == WarningStatus.FAILED and 
                self.send_attempts < 3 and 
                self.last_attempt and 
                (datetime.utcnow() - self.last_attempt).total_seconds() > 300)  # 5 minutes