"""
User Schemas

This module contains Pydantic schemas for User operations.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole, UserStatus
from app.schemas.common import MessageResponse


class UserBase(BaseModel):
    """
    Base user schema with common fields.
    """
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(default=None, max_length=100, description="Full name")


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    password: str = Field(..., min_length=8, max_length=100, description="Password")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    preferences: Optional[dict] = Field(default={}, description="User preferences")


class UserUpdate(BaseModel):
    """
    Schema for updating a user.
    """
    email: Optional[EmailStr] = Field(default=None, description="User email address")
    username: Optional[str] = Field(default=None, min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(default=None, max_length=100, description="Full name")
    role: Optional[UserRole] = Field(default=None, description="User role")
    status: Optional[UserStatus] = Field(default=None, description="Account status")
    preferences: Optional[dict] = Field(default=None, description="User preferences")
    password: Optional[str] = Field(default=None, min_length=8, max_length=100, description="New password")


class UserLogin(BaseModel):
    """
    Schema for user login.
    """
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class UserResponse(UserBase):
    """
    Schema for user response (without sensitive data).
    """
    id: int = Field(..., description="User ID")
    role: UserRole = Field(..., description="User role")
    status: UserStatus = Field(..., description="Account status")
    is_verified: bool = Field(default=False, description="Whether email is verified")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_admin: bool = Field(..., description="Whether user is admin")
    is_active: bool = Field(..., description="Whether account is active")
    
    class Config:
        from_attributes = True


class UserTokenResponse(BaseModel):
    """
    Schema for user authentication token response.
    """
    user: UserResponse = Field(..., description="User information")
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class UserRefreshTokenResponse(BaseModel):
    """
    Schema for token refresh response.
    """
    access_token: str = Field(..., description="New access token")
    refresh_token: str = Field(..., description="New refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class UserDeleteResponse(MessageResponse):
    """
    Schema for user deletion response.
    """
    user_id: int = Field(..., description="Deleted user ID")