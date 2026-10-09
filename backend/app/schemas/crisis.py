"""
Crisis Schemas

This module contains Pydantic schemas for Crisis operations.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.crisis import CrisisSeverity, CrisisStatus, CrisisType
from app.schemas.common import MessageResponse


class CrisisBase(BaseModel):
    """
    Base crisis schema with common fields.
    """
    crisis_type: CrisisType = Field(default=CrisisType.OTHER, description="Type of crisis")
    title: str = Field(..., max_length=200, description="Crisis title")


class CrisisCreate(CrisisBase):
    """
    Schema for creating a new crisis prediction.
    """
    dataset_id: Optional[int] = Field(default=None, description="Reference to dataset")
    severity: CrisisSeverity = Field(default=CrisisSeverity.MEDIUM, description="Severity level")
    description: Optional[str] = Field(default=None, description="Detailed description")
    location: Optional[str] = Field(default=None, max_length=100, description="Geographic location")
    start_date: Optional[datetime] = Field(default=None, description="Start date of crisis")
    end_date: Optional[datetime] = Field(default=None, description="End date of crisis")
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1, description="Confidence score (0-1)")
    impact_score: Optional[float] = Field(default=None, ge=0, le=100, description="Impact score (0-100)")
    parameters: Optional[dict] = Field(default={}, description="Prediction parameters")
    metadata: Optional[dict] = Field(default={}, description="Additional metadata")


class CrisisUpdate(BaseModel):
    """
    Schema for updating a crisis event.
    """
    dataset_id: Optional[int] = Field(default=None, description="Reference to dataset")
    crisis_type: Optional[CrisisType] = Field(default=None, description="Type of crisis")
    severity: Optional[CrisisSeverity] = Field(default=None, description="Severity level")
    status: Optional[CrisisStatus] = Field(default=None, description="Current status")
    title: Optional[str] = Field(default=None, max_length=200, description="Crisis title")
    description: Optional[str] = Field(default=None, description="Detailed description")
    location: Optional[str] = Field(default=None, max_length=100, description="Geographic location")
    start_date: Optional[datetime] = Field(default=None, description="Start date of crisis")
    end_date: Optional[datetime] = Field(default=None, description="End date of crisis")
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1, description="Confidence score (0-1)")
    impact_score: Optional[float] = Field(default=None, ge=0, le=100, description="Impact score (0-100)")
    parameters: Optional[dict] = Field(default=None, description="Prediction parameters")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


class CrisisResponse(CrisisBase):
    """
    Schema for crisis response.
    """
    id: int = Field(..., description="Crisis ID")
    dataset_id: Optional[int] = Field(default=None, description="Reference to dataset")
    severity: CrisisSeverity = Field(..., description="Severity level")
    status: CrisisStatus = Field(..., description="Current status")
    description: Optional[str] = Field(default=None, description="Detailed description")
    location: Optional[str] = Field(default=None, max_length=100, description="Geographic location")
    start_date: Optional[datetime] = Field(default=None, description="Start date of crisis")
    end_date: Optional[datetime] = Field(default=None, description="End date of crisis")
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1, description="Confidence score (0-1)")
    impact_score: Optional[float] = Field(default=None, ge=0, le=100, description="Impact score (0-100)")
    parameters: dict = Field(default={}, description="Prediction parameters")
    metadata: dict = Field(default={}, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Whether crisis is currently active")
    is_high_priority: bool = Field(..., description="Whether crisis is high priority")
    risk_level: str = Field(..., description="Overall risk level")
    
    class Config:
        from_attributes = True