"""
Warnings API

This module provides endpoints for warning and notification management.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.crisis import Crisis
from app.models.user import User
from app.models.warning import Warning, WarningPriority, WarningStatus, WarningType
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.warning import WarningCreate, WarningResponse, WarningUpdate
from app.api.v1.users import get_current_admin_user, get_current_user

router = APIRouter(prefix="/warnings", tags=["warnings"])


@router.post("/", response_model=WarningResponse, status_code=status.HTTP_201_CREATED)
async def create_warning(
    warning_data: WarningCreate,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new warning.
    """
    # Check if user exists (if provided)
    if warning_data.user_id:
        user_result = await db.execute(
            select(User).where(User.id == warning_data.user_id)
        )
        user = user_result.scalars().first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )
    
    # Check if crisis exists (if provided)
    if warning_data.crisis_id:
        crisis_result = await db.execute(
            select(Crisis).where(Crisis.id == warning_data.crisis_id)
        )
        crisis = crisis_result.scalars().first()
        if crisis is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Crisis not found",
            )
    
    new_warning = Warning(
        user_id=warning_data.user_id,
        crisis_id=warning_data.crisis_id,
        warning_type=warning_data.warning_type or WarningType.EMAIL,
        priority=warning_data.priority or WarningPriority.MEDIUM,
        subject=warning_data.subject,
        message=warning_data.message,
        recipient=warning_data.recipient,
        metadata=warning_data.metadata or {},
    )
    
    db.add(new_warning)
    await db.commit()
    await db.refresh(new_warning)
    
    # Add background task to send the warning
    background_tasks.add_task(
        send_warning,
        warning_id=new_warning.id,
        db=db
    )
    
    return WarningResponse.from_orm(new_warning)


@router.get("/", response_model=PaginatedResponse[WarningResponse])
async def list_warnings(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    warning_type: Optional[WarningType] = Query(default=None),
    priority: Optional[WarningPriority] = Query(default=None),
    status: Optional[WarningStatus] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    crisis_id: Optional[int] = Query(default=None),
    is_read: Optional[bool] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all warnings with pagination and filtering.
    
    Regular users can only see their own warnings.
    Admins can see all warnings.
    """
    offset = (page - 1) * size
    
    query = select(Warning)
    
    # Filter by current user if not admin
    if not current_user.is_admin:
        query = query.where(Warning.user_id == current_user.id)
    
    # Additional filters
    if warning_type:
        query = query.where(Warning.warning_type == warning_type)
    if priority:
        query = query.where(Warning.priority == priority)
    if status:
        query = query.where(Warning.status == status)
    if user_id:
        if current_user.is_admin:
            query = query.where(Warning.user_id == user_id)
    if crisis_id:
        query = query.where(Warning.crisis_id == crisis_id)
    if is_read is not None:
        query = query.where(Warning.is_read == is_read)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(Warning.subject.ilike(search_pattern))
    
    # Get total count
    count_result = await db.execute(
        select(Warning).where(*query.whereclause.clauses if query.whereclause else True)
    )
    total = len(count_result.scalars().all())
    
    # Get paginated results
    result = await db.execute(query.order_by(desc(Warning.created_at)).offset(offset).limit(size))
    warnings = result.scalars().all()
    
    return PaginatedResponse[WarningResponse](
        items=[WarningResponse.from_orm(warning) for warning in warnings],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
        has_next=offset + size < total,
        has_previous=page > 1
    )


@router.get("/{warning_id}", response_model=WarningResponse)
async def get_warning(
    warning_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific warning by ID.
    
    Regular users can only access their own warnings.
    """
    result = await db.execute(
        select(Warning).where(Warning.id == warning_id)
    )
    warning = result.scalars().first()
    
    if warning is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warning not found",
        )
    
    # Check permissions
    if not current_user.is_admin and warning.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    return WarningResponse.from_orm(warning)


@router.put("/{warning_id}", response_model=WarningResponse)
async def update_warning(
    warning_id: int,
    warning_data: WarningUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a warning.
    """
    result = await db.execute(
        select(Warning).where(Warning.id == warning_id)
    )
    warning = result.scalars().first()
    
    if warning is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warning not found",
        )
    
    # Check permissions
    if not current_user.is_admin and warning.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    # Update warning data
    if warning_data.user_id and current_user.is_admin:
        warning.user_id = warning_data.user_id
    if warning_data.crisis_id:
        warning.crisis_id = warning_data.crisis_id
    if warning_data.warning_type:
        warning.warning_type = warning_data.warning_type
    if warning_data.priority:
        warning.priority = warning_data.priority
    if warning_data.status:
        warning.status = warning_data.status
    if warning_data.subject:
        warning.subject = warning_data.subject
    if warning_data.message:
        warning.message = warning_data.message
    if warning_data.recipient:
        warning.recipient = warning_data.recipient
    if warning_data.is_read is not None:
        warning.is_read = warning_data.is_read
    if warning_data.metadata is not None:
        warning.metadata = warning_data.metadata
    
    warning.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(warning)
    
    return WarningResponse.from_orm(warning)


@router.delete("/{warning_id}", response_model=MessageResponse)
async def delete_warning(
    warning_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a warning.
    """
    result = await db.execute(
        select(Warning).where(Warning.id == warning_id)
    )
    warning = result.scalars().first()
    
    if warning is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warning not found",
        )
    
    # Check permissions
    if not current_user.is_admin and warning.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    await db.delete(warning)
    await db.commit()
    
    return MessageResponse(
        message="Warning deleted successfully",
        success=True,
        details=f"Warning {warning_id} has been deleted"
    )


@router.post("/{warning_id}/read", response_model=WarningResponse)
async def mark_warning_read(
    warning_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a warning as read.
    """
    result = await db.execute(
        select(Warning).where(Warning.id == warning_id)
    )
    warning = result.scalars().first()
    
    if warning is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warning not found",
        )
    
    # Check permissions
    if not current_user.is_admin and warning.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    warning.is_read = True
    warning.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(warning)
    
    return WarningResponse.from_orm(warning)


@router.post("/{warning_id}/retry", response_model=WarningResponse)
async def retry_warning(
    warning_id: int,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Retry sending a failed warning.
    """
    result = await db.execute(
        select(Warning).where(Warning.id == warning_id)
    )
    warning = result.scalars().first()
    
    if warning is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warning not found",
        )
    
    if not warning.should_retry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Warning cannot be retried",
        )
    
    # Update status to pending
    warning.status = WarningStatus.PENDING
    warning.send_attempts = 0
    warning.error_message = None
    warning.last_attempt = None
    warning.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(warning)
    
    # Add background task to retry sending
    background_tasks.add_task(
        send_warning,
        warning_id=warning.id,
        db=db
    )
    
    return WarningResponse.from_orm(warning)


async def send_warning(warning_id: int, db: AsyncSession):
    """
    Background task to send a warning via the specified channel.
    
    This is a placeholder function. In production, you would implement
    actual notification sending logic (email, SMS, push notifications, etc.).
    """
    import asyncio
    from sqlalchemy import update
    
    try:
        # Get the warning
        result = await db.execute(
            select(Warning).where(Warning.id == warning_id)
        )
        warning = result.scalars().first()
        
        if warning is None:
            return
        
        # Simulate sending delay
        await asyncio.sleep(1)
        
        # Update warning status
        await db.execute(
            update(Warning)
            .where(Warning.id == warning_id)
            .values(
                status=WarningStatus.DELIVERED,
                send_attempts=warning.send_attempts + 1,
                last_attempt=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()
        
    except Exception as e:
        # Update warning with error
        await db.execute(
            update(Warning)
            .where(Warning.id == warning_id)
            .values(
                status=WarningStatus.FAILED,
                send_attempts=warning.send_attempts + 1,
                last_attempt=datetime.utcnow(),
                error_message=str(e),
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()