"""
Users API

This module provides endpoints for user management.
"""

from datetime import timedelta
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import security
from app.models.user import User, UserRole, UserStatus
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserRefreshTokenResponse,
    UserResponse,
    UserTokenResponse,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current user from the JWT token.
    """
    payload = security.decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive",
        )
    
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current user and verify admin role.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


@router.post("/register", response_model=UserTokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Creates a new user account and returns authentication tokens.
    """
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Hash password
    hashed_password = security.hash_password(user_data.password)
    
    # Create user
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        preferences=user_data.preferences or {},
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Generate tokens
    token_data = {"sub": str(new_user.id), "username": new_user.username, "role": new_user.role}
    access_token = security.create_access_token(token_data)
    refresh_token = security.create_refresh_token(token_data)
    
    return UserTokenResponse(
        user=UserResponse.from_orm(new_user),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/token", response_model=UserTokenResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access tokens.
    
    Uses OAuth2 password flow for authentication.
    """
    # Find user by username
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Generate tokens
    token_data = {"sub": str(user.id), "username": user.username, "role": user.role}
    access_token = security.create_access_token(token_data)
    refresh_token = security.create_refresh_token(token_data)
    
    return UserTokenResponse(
        user=UserResponse.from_orm(user),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=UserRefreshTokenResponse)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    payload = security.decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Verify user still exists
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive",
        )
    
    # Generate new tokens
    token_data = {"sub": str(user.id), "username": user.username, "role": user.role}
    new_access_token = security.create_access_token(token_data)
    new_refresh_token = security.create_refresh_token(token_data)
    
    return UserRefreshTokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    """
    return UserResponse.from_orm(current_user)


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    role: Optional[UserRole] = Query(default=None),
    status: Optional[UserStatus] = Query(default=None),
    search: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all users with pagination.
    
    Admin-only endpoint.
    """
    offset = (page - 1) * size
    
    # Build query
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    if status:
        query = query.where(User.status == status)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            User.username.ilike(search_pattern) |
            User.email.ilike(search_pattern) |
            User.full_name.ilike(search_pattern)
        )
    
    # Get total count
    count_result = await db.execute(
        select(User).where(*query.whereclause.clauses if query.whereclause else True)
    )
    total = len(count_result.scalars().all())
    
    # Get paginated results
    result = await db.execute(query.offset(offset).limit(size))
    users = result.scalars().all()
    
    return PaginatedResponse[UserResponse](
        items=[UserResponse.from_orm(user) for user in users],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
        has_next=offset + size < total,
        has_previous=page > 1
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific user by ID.
    
    Users can get their own info, admins can get any user.
    """
    # Check permissions
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a user.
    
    Users can update their own info, admins can update any user.
    """
    # Check permissions
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update user data
    if user_data.email:
        user.email = user_data.email
    if user_data.username:
        user.username = user_data.username
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.role and current_user.is_admin:
        user.role = user_data.role
    if user_data.status and current_user.is_admin:
        user.status = user_data.status
    if user_data.preferences is not None:
        user.preferences = user_data.preferences
    if user_data.password:
        user.hashed_password = security.hash_password(user_data.password)
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.from_orm(user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a user.
    
    Admin-only endpoint.
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    await db.delete(user)
    await db.commit()
    
    return MessageResponse(
        message="User deleted successfully",
        success=True,
        details=f"User {user_id} has been deleted"
    )