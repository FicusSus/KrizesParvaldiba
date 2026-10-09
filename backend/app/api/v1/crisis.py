"""
Crisis API

This module provides endpoints for crisis prediction and management.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.crisis import Crisis, CrisisSeverity, CrisisStatus, CrisisType
from app.models.dataset import Dataset
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.crisis import CrisisCreate, CrisisResponse, CrisisUpdate
from app.api.v1.users import get_current_admin_user, get_current_user
from app.models.user import User

router = APIRouter(prefix="/crisis", tags=["crisis"])


@router.post("/predict", response_model=CrisisResponse, status_code=status.HTTP_201_CREATED)
async def predict_crisis(
    crisis_data: CrisisCreate,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new crisis prediction.
    
    This endpoint can trigger crisis prediction based on provided data
    or existing datasets.
    """
    # Check if dataset exists (if provided)
    if crisis_data.dataset_id:
        dataset_result = await db.execute(
            select(Dataset).where(Dataset.id == crisis_data.dataset_id)
        )
        dataset = dataset_result.scalars().first()
        if dataset is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset not found",
            )
    
    # Create crisis prediction
    new_crisis = Crisis(
        dataset_id=crisis_data.dataset_id,
        crisis_type=crisis_data.crisis_type or CrisisType.OTHER,
        severity=crisis_data.severity or CrisisSeverity.MEDIUM,
        status=CrisisStatus.PREDICATED,
        title=crisis_data.title,
        description=crisis_data.description,
        location=crisis_data.location,
        start_date=crisis_data.start_date,
        end_date=crisis_data.end_date,
        confidence_score=crisis_data.confidence_score,
        impact_score=crisis_data.impact_score,
        parameters=crisis_data.parameters or {},
        metadata=crisis_data.metadata or {},
    )
    
    db.add(new_crisis)
    await db.commit()
    await db.refresh(new_crisis)
    
    # Add background task to run prediction models
    background_tasks.add_task(
        run_crisis_prediction,
        crisis_id=new_crisis.id,
        db=db
    )
    
    return CrisisResponse.from_orm(new_crisis)


@router.get("/", response_model=PaginatedResponse[CrisisResponse])
async def list_crisis_events(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    crisis_type: Optional[CrisisType] = Query(default=None),
    severity: Optional[CrisisSeverity] = Query(default=None),
    status: Optional[CrisisStatus] = Query(default=None),
    dataset_id: Optional[int] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all crisis events with pagination and filtering.
    """
    offset = (page - 1) * size
    
    query = select(Crisis)
    
    if crisis_type:
        query = query.where(Crisis.crisis_type == crisis_type)
    if severity:
        query = query.where(Crisis.severity == severity)
    if status:
        query = query.where(Crisis.status == status)
    if dataset_id:
        query = query.where(Crisis.dataset_id == dataset_id)
    if is_active is not None:
        if is_active:
            query = query.where(Crisis.status.in_([
                CrisisStatus.PREDICATED, 
                CrisisStatus.CONFIRMED, 
                CrisisStatus.ONGOING
            ]))
        else:
            query = query.where(Crisis.status.notin_([
                CrisisStatus.PREDICATED, 
                CrisisStatus.CONFIRMED, 
                CrisisStatus.ONGOING
            ]))
    if search:
        search_pattern = f"%{search}%"
        query = query.where(Crisis.title.ilike(search_pattern))
    
    # Get total count
    count_result = await db.execute(
        select(Crisis).where(*query.whereclause.clauses if query.whereclause else True)
    )
    total = len(count_result.scalars().all())
    
    # Get paginated results
    result = await db.execute(query.order_by(desc(Crisis.created_at)).offset(offset).limit(size))
    crises = result.scalars().all()
    
    return PaginatedResponse[CrisisResponse](
        items=[CrisisResponse.from_orm(crisis) for crisis in crises],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
        has_next=offset + size < total,
        has_previous=page > 1
    )


@router.get("/{crisis_id}", response_model=CrisisResponse)
async def get_crisis(
    crisis_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific crisis event by ID.
    """
    result = await db.execute(
        select(Crisis).where(Crisis.id == crisis_id)
    )
    crisis = result.scalars().first()
    
    if crisis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crisis event not found",
        )
    
    return CrisisResponse.from_orm(crisis)


@router.put("/{crisis_id}", response_model=CrisisResponse)
async def update_crisis(
    crisis_id: int,
    crisis_data: CrisisUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a crisis event.
    """
    result = await db.execute(
        select(Crisis).where(Crisis.id == crisis_id)
    )
    crisis = result.scalars().first()
    
    if crisis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crisis event not found",
        )
    
    # Update crisis data
    if crisis_data.crisis_type:
        crisis.crisis_type = crisis_data.crisis_type
    if crisis_data.severity:
        crisis.severity = crisis_data.severity
    if crisis_data.status:
        crisis.status = crisis_data.status
    if crisis_data.title:
        crisis.title = crisis_data.title
    if crisis_data.description is not None:
        crisis.description = crisis_data.description
    if crisis_data.location is not None:
        crisis.location = crisis_data.location
    if crisis_data.start_date:
        crisis.start_date = crisis_data.start_date
    if crisis_data.end_date:
        crisis.end_date = crisis_data.end_date
    if crisis_data.confidence_score is not None:
        crisis.confidence_score = crisis_data.confidence_score
    if crisis_data.impact_score is not None:
        crisis.impact_score = crisis_data.impact_score
    if crisis_data.parameters is not None:
        crisis.parameters = crisis_data.parameters
    if crisis_data.metadata is not None:
        crisis.metadata = crisis_data.metadata
    
    await db.commit()
    await db.refresh(crisis)
    
    return CrisisResponse.from_orm(crisis)


@router.delete("/{crisis_id}", response_model=MessageResponse)
async def delete_crisis(
    crisis_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a crisis event.
    """
    result = await db.execute(
        select(Crisis).where(Crisis.id == crisis_id)
    )
    crisis = result.scalars().first()
    
    if crisis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crisis event not found",
        )
    
    await db.delete(crisis)
    await db.commit()
    
    return MessageResponse(
        message="Crisis event deleted successfully",
        success=True,
        details=f"Crisis {crisis_id} has been deleted"
    )


@router.post("/{crisis_id}/confirm", response_model=CrisisResponse)
async def confirm_crisis(
    crisis_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Confirm a predicted crisis event.
    
    Changes the status from PREDICATED to CONFIRMED.
    """
    result = await db.execute(
        select(Crisis).where(Crisis.id == crisis_id)
    )
    crisis = result.scalars().first()
    
    if crisis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crisis event not found",
        )
    
    if crisis.status != CrisisStatus.PREDICATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only predicted crises can be confirmed",
        )
    
    crisis.status = CrisisStatus.CONFIRMED
    crisis.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(crisis)
    
    return CrisisResponse.from_orm(crisis)


@router.post("/{crisis_id}/resolve", response_model=CrisisResponse)
async def resolve_crisis(
    crisis_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Mark a crisis event as resolved.
    """
    result = await db.execute(
        select(Crisis).where(Crisis.id == crisis_id)
    )
    crisis = result.scalars().first()
    
    if crisis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crisis event not found",
        )
    
    crisis.status = CrisisStatus.RESOLVED
    crisis.end_date = datetime.utcnow()
    crisis.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(crisis)
    
    return CrisisResponse.from_orm(crisis)


@router.post("/{crisis_id}/false-alarm", response_model=CrisisResponse)
async def mark_false_alarm(
    crisis_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Mark a crisis event as false alarm.
    """
    result = await db.execute(
        select(Crisis).where(Crisis.id == crisis_id)
    )
    crisis = result.scalars().first()
    
    if crisis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crisis event not found",
        )
    
    crisis.status = CrisisStatus.FALSE_ALARM
    crisis.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(crisis)
    
    return CrisisResponse.from_orm(crisis)


async def run_crisis_prediction(crisis_id: int, db: AsyncSession):
    """
    Background task to run crisis prediction models.
    
    This is a placeholder function. In production, you would implement
    actual ML model prediction logic here.
    """
    import asyncio
    from sqlalchemy import update
    from app.models.prediction import Prediction, PredictionStatus, PredictionType, ModelType
    
    try:
        # Get the crisis
        result = await db.execute(
            select(Crisis).where(Crisis.id == crisis_id)
        )
        crisis = result.scalars().first()
        
        if crisis is None:
            return
        
        # Simulate model prediction
        await asyncio.sleep(5)
        
        # Update crisis with prediction results (simulated)
        await db.execute(
            update(Crisis)
            .where(Crisis.id == crisis_id)
            .values(
                severity=CrisisSeverity.HIGH,  # Simulated prediction
                confidence_score=0.85,  # Simulated confidence
                impact_score=75.0,  # Simulated impact
                updated_at=datetime.utcnow()
            )
        )
        
        # Create prediction record
        new_prediction = Prediction(
            dataset_id=crisis.dataset_id,
            model_type=ModelType.CRISIS_DETECTION,
            prediction_type=PredictionType.CLASSIFICATION,
            status=PredictionStatus.COMPLETED,
            model_version="1.0",
            model_parameters={},
            predictions={"crisis_type": crisis.crisis_type, "severity": "high"},
            metrics={"accuracy": 0.92, "f1_score": 0.88},
            training_time=10.5,
            prediction_time=2.3,
            metadata={"crisis_id": crisis_id},
        )
        
        db.add(new_prediction)
        await db.commit()
        
    except Exception as e:
        # Update crisis with error
        await db.execute(
            update(Crisis)
            .where(Crisis.id == crisis_id)
            .values(
                error_message=str(e),
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()