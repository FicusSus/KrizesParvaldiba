"""
Prediction Schema

This module contains Pydantic schemas for crisis prediction models and results.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import MessageResponse


class PredictionBase(BaseModel):
    """Base prediction schema with common fields."""
    
    crisis_id: Optional[int] = Field(
        default=None,
        description="Reference to the crisis this prediction relates to"
    )
    dataset_id: Optional[int] = Field(
        default=None,
        description="Reference to the dataset used for prediction"
    )
    model_type: str = Field(
        ...,
        max_length=50,
        description="Type of prediction model used"
    )
    model_version: str = Field(
        ...,
        max_length=50,
        description="Version of the prediction model"
    )
    prediction_type: str = Field(
        ...,
        max_length=50,
        description="Type of prediction (crisis_detection, severity, timeline, impact)"
    )


class PredictionCreate(PredictionBase):
    """Schema for creating a new prediction."""
    
    parameters: Optional[Dict[str, Any]] = Field(
        default={},
        description="Model parameters used for prediction"
    )
    results: Optional[Dict[str, Any]] = Field(
        default={},
        description="Raw prediction results"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score of the prediction"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "crisis_id": 1,
                "dataset_id": 1,
                "model_type": "random_forest",
                "model_version": "1.0.0",
                "prediction_type": "crisis_detection",
                "parameters": {"n_estimators": 100},
                "results": {"prediction": "crisis", "probability": 0.95},
                "confidence_score": 0.95
            }
        }


class PredictionUpdate(BaseModel):
    """Schema for updating a prediction."""
    
    crisis_id: Optional[int] = Field(
        default=None,
        description="Reference to the crisis"
    )
    dataset_id: Optional[int] = Field(
        default=None,
        description="Reference to the dataset"
    )
    model_type: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Type of prediction model"
    )
    model_version: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Version of the prediction model"
    )
    prediction_type: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Type of prediction"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Model parameters"
    )
    results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Prediction results"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score"
    )
    status: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Prediction status"
    )


class PredictionResponse(PredictionBase):
    """Schema for prediction response with all fields."""
    
    id: int = Field(
        ...,
        description="Unique identifier for the prediction"
    )
    parameters: Dict[str, Any] = Field(
        default={},
        description="Model parameters used"
    )
    results: Dict[str, Any] = Field(
        default={},
        description="Prediction results"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score of the prediction"
    )
    status: str = Field(
        ...,
        max_length=20,
        description="Prediction status (pending, completed, failed)"
    )
    execution_time: Optional[float] = Field(
        default=None,
        description="Time taken to execute the prediction in seconds"
    )
    error_message: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Error message if prediction failed"
    )
    extra_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional prediction data"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when prediction was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when prediction was last updated"
    )
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "crisis_id": 1,
                "dataset_id": 1,
                "model_type": "random_forest",
                "model_version": "1.0.0",
                "prediction_type": "crisis_detection",
                "parameters": {"n_estimators": 100},
                "results": {"prediction": "crisis", "probability": 0.95},
                "confidence_score": 0.95,
                "status": "completed",
                "execution_time": 2.5,
                "error_message": None,
                "extra_data": {},
                "created_at": "2026-10-09T10:00:00Z",
                "updated_at": "2026-10-09T10:00:00Z"
            }
        }
