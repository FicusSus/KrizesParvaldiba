"""
Data Source Model

This module contains models for data sources and datasets.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class DataSourceType(str, enum.Enum):
    """Types of data sources."""
    CSV = "csv"
    JSON = "json"
    API = "api"
    DATABASE = "database"
    EXCEL = "excel"
    PARQUET = "parquet"


class DataSource(Base):
    """
    Data Source model representing external data sources.
    
    Attributes:
        id: Unique identifier
        name: Data source name
        source_type: Type of data source
        connection_string: Connection string or URL
        description: Description of the data source
        config: Configuration as JSON
        is_active: Whether the data source is active
        last_sync: Last synchronization timestamp
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "data_sources"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[DataSourceType] = mapped_column(
        Enum(DataSourceType),
        nullable=False
    )
    connection_string: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    config: Mapped[Optional[dict]] = mapped_column(Text, default={})
    is_active: Mapped[bool] = mapped_column(Integer, default=True, nullable=False)
    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime)
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
    datasets: Mapped[List["Dataset"]] = relationship(
        "Dataset",
        back_populates="data_source",
        foreign_keys="Dataset.data_source_id"
    )
    
    def __repr__(self) -> str:
        return f"DataSource(id={self.id}, name={self.name}, type={self.source_type})"
    
    @property
    def is_available(self) -> bool:
        """Check if data source is available for use."""
        return self.is_active and self.connection_string