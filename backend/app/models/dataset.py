"""
Dataset Model

This module contains models for datasets and data processing.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.data_source import DataSource
    from app.models.crisis import Crisis
    from app.models.prediction import Prediction


class DatasetStatus(str, enum.Enum):
    """Dataset processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class DatasetType(str, enum.Enum):
    """Types of datasets."""
    RAW = "raw"
    PROCESSED = "processed"
    AGGREGATED = "aggregated"
    FEATURES = "features"


class Dataset(Base):
    """
    Dataset model representing ingested and processed data.
    
    Attributes:
        id: Unique identifier
        data_source_id: Reference to data source
        name: Dataset name
        file_path: Path to the data file
        dataset_type: Type of dataset
        status: Processing status
        row_count: Number of rows in the dataset
        column_count: Number of columns
        file_size: File size in bytes
        metadata: Additional metadata as JSON
        processing_time: Time taken to process in seconds
        error_message: Error message if processing failed
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "datasets"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data_source_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("data_sources.id", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    dataset_type: Mapped[DatasetType] = mapped_column(
        Enum(DatasetType),
        default=DatasetType.RAW,
        nullable=False
    )
    status: Mapped[DatasetStatus] = mapped_column(
        Enum(DatasetStatus),
        default=DatasetStatus.PENDING,
        nullable=False
    )
    row_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    column_count: Mapped[Optional[int]] = mapped_column(Integer)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)  # bytes
    metadata: Mapped[Optional[dict]] = mapped_column(Text, default={})
    processing_time: Mapped[Optional[float]] = mapped_column(Float)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
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
    data_source: Mapped[Optional["DataSource"]] = relationship(
        "DataSource",
        back_populates="datasets"
    )
    crisis_events: Mapped[List["Crisis"]] = relationship(
        "Crisis",
        back_populates="dataset",
        foreign_keys="Crisis.dataset_id"
    )
    predictions: Mapped[List["Prediction"]] = relationship(
        "Prediction",
        back_populates="dataset",
        foreign_keys="Prediction.dataset_id"
    )
    
    def __repr__(self) -> str:
        return f"Dataset(id={self.id}, name={self.name}, status={self.status})"
    
    @property
    def is_processed(self) -> bool:
        """Check if dataset has been successfully processed."""
        return self.status == DatasetStatus.COMPLETED
    
    @property
    def is_processing(self) -> bool:
        """Check if dataset is currently processing."""
        return self.status == DatasetStatus.PROCESSING