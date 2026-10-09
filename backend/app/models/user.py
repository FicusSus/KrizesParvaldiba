"""
User Model

This module contains the User model and related database entities.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.warning import Warning
    from app.models.notification import Notification


class UserRole(str, enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"
    ANALYST = "analyst"
    USER = "user"


class UserStatus(str, enum.Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(Base):
    """
    User model representing system users.
    
    Attributes:
        id: Unique identifier
        email: User email (unique)
        username: User username (unique)
        hashed_password: Hashed password
        full_name: User's full name
        role: User role
        status: Account status
        api_key_hash: Hashed API key for programmatic access
        preferences: User preferences as JSON
        is_verified: Whether email is verified
        last_login: Last login timestamp
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), 
        default=UserRole.USER,
        nullable=False
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus),
        default=UserStatus.ACTIVE,
        nullable=False
    )
    api_key_hash: Mapped[Optional[str]] = mapped_column(String(255))
    preferences: Mapped[Optional[dict]] = mapped_column(Text, default={})
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
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
    warnings: Mapped[List["Warning"]] = relationship(
        "Warning",
        back_populates="user",
        foreign_keys="Warning.user_id"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        foreign_keys="Notification.user_id"
    )
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, username={self.username})"
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.status == UserStatus.ACTIVE