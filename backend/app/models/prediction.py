"""
Prediction Model

This module contains models for ML predictions and model runs.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class PredictionStatus(str, enum.Enum):
    """Status of prediction runs."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PredictionType(str, enum.Enum):
    """Types of predictions."""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    TIME_SERIES = "time_series"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"


class ModelType(str, enum.Enum):
    """Types of ML models."""
    CRISIS_DETECTION = "crisis_detection"
    SEVERITY_PREDICTION = "severity_prediction"
    TIMELINE_PREDICTION = "timeline_prediction"
    IMPACT_ASSESSMENT = "impact_assessment"


class Prediction(Base):
    """
    Prediction model representing ML model runs and predictions.
    
    Attributes:
        id: Unique identifier
        dataset_id: Reference to the dataset used for prediction
        model_type: Type of ML model
        prediction_type: Type of prediction
        status: Current status
        model_version: Version of the model used
        model_parameters: Parameters used for the model as JSON
        feature_columns: List of feature columns used
        target_column: Target column for supervised learning
        predictions: Prediction results as JSON
        metrics: Evaluation metrics as JSON
        training_time: Time taken to train in seconds
        prediction_time: Time taken to predict in seconds
        error_message: Error message if prediction failed
        metadata: Additional metadata as JSON
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "predictions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dataset_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL")
    )
    model_type: Mapped[ModelType] = mapped_column(
        Enum(ModelType),
        nullable=False
    )
    prediction_type: Mapped[PredictionType] = mapped_column(
        Enum(PredictionType),
        default=PredictionType.CLASSIFICATION,
        nullable=False
    )
    status: Mapped[PredictionStatus] = mapped_column(
        Enum(PredictionStatus),
        default=PredictionStatus.PENDING,
        nullable=False
    )
    model_version: Mapped[str] = mapped_column(String(50), default="1.0")
    model_parameters: Mapped[Optional[dict]] = mapped_column(Text, default={})
    feature_columns: Mapped[Optional[list]] = mapped_column(Text, default=[])
    target_column: Mapped[Optional[str]] = mapped_column(String(100))
    predictions: Mapped[Optional[dict]] = mapped_column(Text, default={})
    metrics: Mapped[Optional[dict]] = mapped_column(Text, default={})
    training_time: Mapped[Optional[float]] = mapped_column(Float)
    prediction_time: Mapped[Optional[float]] = mapped_column(Float)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
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
    dataset: Mapped[Optional["Dataset"]] = relationship(
        "Dataset",
        back_populates="predictions"
    )
    
    def __repr__(self) -> str:
        return f"Prediction(id={self.id}, model={self.model_type}, status={self.status})"
    
    @property
    def is_successful(self) -> bool:
        """Check if prediction completed successfully."""
        return self.status == PredictionStatus.COMPLETED
    
    @property
    def is_running(self) -> bool:
        """Check if prediction is currently running."""
        return self.status in [PredictionStatus.PENDING, PredictionStatus.RUNNING]
    
    @property
    def accuracy(self) -> Optional[float]:
        """Get accuracy metric if available."""
        if self.metrics:
            return self.metrics.get("accuracy")
        return None
    
    @property
    def f1_score(self) -> Optional[float]:
        """Get F1 score metric if available."""
        if self.metrics:
            return self.metrics.get("f1_score")
        return None