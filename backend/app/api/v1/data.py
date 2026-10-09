"""
Data API

This module provides endpoints for data source and dataset management.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, UploadFile

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.data_source import DataSource, DataSourceType
from app.models.dataset import Dataset, DatasetStatus, DatasetType
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.data_source import DataSourceCreate, DataSourceResponse, DataSourceUpdate
from app.schemas.dataset import DatasetCreate, DatasetResponse, DatasetUpdate
from app.api.v1.users import get_current_admin_user, get_current_user
from app.models.user import User

router = APIRouter(prefix="/data", tags=["data"])


@router.post("/sources", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_data_source(
    data_source: DataSourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new data source.
    """
    new_source = DataSource(
        name=data_source.name,
        source_type=data_source.source_type,
        connection_string=data_source.connection_string,
        description=data_source.description,
        config=data_source.config or {},
        is_active=data_source.is_active,
    )
    
    db.add(new_source)
    await db.commit()
    await db.refresh(new_source)
    
    return DataSourceResponse.from_orm(new_source)


@router.get("/sources", response_model=PaginatedResponse[DataSourceResponse])
async def list_data_sources(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    source_type: Optional[DataSourceType] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all data sources with pagination.
    """
    offset = (page - 1) * size
    
    query = select(DataSource)
    
    if source_type:
        query = query.where(DataSource.source_type == source_type)
    if is_active is not None:
        query = query.where(DataSource.is_active == is_active)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            DataSource.name.ilike(search_pattern) |
            DataSource.description.ilike(search_pattern)
        )
    
    # Get total count
    count_result = await db.execute(
        select(DataSource).where(*query.whereclause.clauses if query.whereclause else True)
    )
    total = len(count_result.scalars().all())
    
    # Get paginated results
    result = await db.execute(query.order_by(desc(DataSource.created_at)).offset(offset).limit(size))
    sources = result.scalars().all()
    
    return PaginatedResponse[DataSourceResponse](
        items=[DataSourceResponse.from_orm(source) for source in sources],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
        has_next=offset + size < total,
        has_previous=page > 1
    )


@router.get("/sources/{source_id}", response_model=DataSourceResponse)
async def get_data_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific data source by ID.
    """
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id)
    )
    source = result.scalars().first()
    
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )
    
    return DataSourceResponse.from_orm(source)


@router.put("/sources/{source_id}", response_model=DataSourceResponse)
async def update_data_source(
    source_id: int,
    data_source: DataSourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a data source.
    """
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id)
    )
    source = result.scalars().first()
    
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )
    
    if data_source.name:
        source.name = data_source.name
    if data_source.source_type:
        source.source_type = data_source.source_type
    if data_source.connection_string:
        source.connection_string = data_source.connection_string
    if data_source.description is not None:
        source.description = data_source.description
    if data_source.config is not None:
        source.config = data_source.config
    if data_source.is_active is not None:
        source.is_active = data_source.is_active
    
    await db.commit()
    await db.refresh(source)
    
    return DataSourceResponse.from_orm(source)


@router.delete("/sources/{source_id}", response_model=MessageResponse)
async def delete_data_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a data source.
    """
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id)
    )
    source = result.scalars().first()
    
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )
    
    await db.delete(source)
    await db.commit()
    
    return MessageResponse(
        message="Data source deleted successfully",
        success=True,
        details=f"Data source {source_id} has been deleted"
    )


@router.post("/datasets", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    dataset: DatasetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new dataset entry.
    """
    # Check if data source exists
    if dataset.data_source_id:
        source_result = await db.execute(
            select(DataSource).where(DataSource.id == dataset.data_source_id)
        )
        if source_result.scalars().first() is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data source not found",
            )
    
    new_dataset = Dataset(
        data_source_id=dataset.data_source_id,
        name=dataset.name,
        file_path=dataset.file_path,
        dataset_type=dataset.dataset_type or DatasetType.RAW,
        status=dataset.status or DatasetStatus.PENDING,
        metadata=dataset.metadata or {},
    )
    
    db.add(new_dataset)
    await db.commit()
    await db.refresh(new_dataset)
    
    return DatasetResponse.from_orm(new_dataset)


@router.get("/datasets", response_model=PaginatedResponse[DatasetResponse])
async def list_datasets(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    dataset_type: Optional[DatasetType] = Query(default=None),
    status: Optional[DatasetStatus] = Query(default=None),
    data_source_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all datasets with pagination.
    """
    offset = (page - 1) * size
    
    query = select(Dataset)
    
    if dataset_type:
        query = query.where(Dataset.dataset_type == dataset_type)
    if status:
        query = query.where(Dataset.status == status)
    if data_source_id:
        query = query.where(Dataset.data_source_id == data_source_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(Dataset.name.ilike(search_pattern))
    
    # Get total count
    count_result = await db.execute(
        select(Dataset).where(*query.whereclause.clauses if query.whereclause else True)
    )
    total = len(count_result.scalars().all())
    
    # Get paginated results
    result = await db.execute(query.order_by(desc(Dataset.created_at)).offset(offset).limit(size))
    datasets = result.scalars().all()
    
    return PaginatedResponse[DatasetResponse](
        items=[DatasetResponse.from_orm(dataset) for dataset in datasets],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
        has_next=offset + size < total,
        has_previous=page > 1
    )


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific dataset by ID.
    """
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalars().first()
    
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )
    
    return DatasetResponse.from_orm(dataset)


@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_type: DatasetType = Form(DatasetType.RAW),
    data_source_id: Optional[int] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a dataset file and create a dataset entry.
    """
    # Validate file extension
    allowed_extensions = {".csv", ".json", ".parquet", ".xlsx", ".xls"}
    file_extension = Path(file.filename or "").suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: {', '.join(sorted(allowed_extensions))}",
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = settings.DATA_DIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}",
        )
    
    # Check if data source exists
    if data_source_id:
        source_result = await db.execute(
            select(DataSource).where(DataSource.id == data_source_id)
        )
        if source_result.scalars().first() is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data source not found",
            )
    
    # Create dataset entry
    new_dataset = Dataset(
        data_source_id=data_source_id,
        name=Path(file.filename).stem,
        file_path=str(file_path),
        dataset_type=dataset_type,
        status=DatasetStatus.PENDING,
        metadata={
            "uploaded_by": current_user.id,
            "original_filename": file.filename,
            "file_size": os.path.getsize(file_path),
        },
    )
    
    db.add(new_dataset)
    await db.commit()
    await db.refresh(new_dataset)
    
    # Add background task to process the dataset
    background_tasks.add_task(
        process_uploaded_dataset,
        dataset_id=new_dataset.id,
        file_path=str(file_path),
        db=db
    )
    
    return DatasetResponse.from_orm(new_dataset)


async def process_uploaded_dataset(dataset_id: int, file_path: str, db: AsyncSession):
    """
    Background task to process uploaded dataset.
    
    This is a placeholder function. In production, you would implement
    actual data processing logic here.
    """
    import asyncio
    from sqlalchemy import update
    
    try:
        # Update dataset status to processing
        await db.execute(
            update(Dataset)
            .where(Dataset.id == dataset_id)
            .values(status=DatasetStatus.PROCESSING, updated_at=datetime.utcnow())
        )
        await db.commit()
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Update dataset status to completed (in real implementation, this would
        # be based on actual processing results)
        await db.execute(
            update(Dataset)
            .where(Dataset.id == dataset_id)
            .values(
                status=DatasetStatus.COMPLETED,
                row_count=1000,  # Placeholder
                column_count=10,  # Placeholder
                processing_time=2.5,  # Placeholder
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()
        
    except Exception as e:
        # Update dataset status to failed
        await db.execute(
            update(Dataset)
            .where(Dataset.id == dataset_id)
            .values(
                status=DatasetStatus.FAILED,
                error_message=str(e),
                updated_at=datetime.utcnow()
            )
        )
        await db.commit()