"""
Crisis Model

This module contains models for crisis events and predictions.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.warning import Warning


class CrisisSeverity(str, enum.Enum):
    """Severity levels for crisis events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CrisisType(str, enum.Enum):
    """Types of crisis events."""
    FINANCIAL = "financial"
    ECONOMIC = "economic"
    POLITICAL = "political"
    SOCIAL = "social"
    ENVIRONMENTAL = "environmental"
    HEALTH = "health"
    SECURITY = "security"
    OTHER = "other"


class CrisisStatus(str, enum.Enum):
    """Status of crisis events."""
    PREDICATED = "predicted"
    CONFIRMED = "confirmed"
    ONGOING = "ongoing"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"


class Crisis(Base):
    """
    Crisis model representing detected or predicted crisis events.
    
    Attributes:
        id: Unique identifier
        dataset_id: Reference to the dataset that triggered the crisis
        crisis_type: Type of crisis
        severity: Severity level
        status: Current status
        title: Crisis title
        description: Detailed description
        location: Geographic location (if applicable)
        start_date: When the crisis started or is predicted to start
        end_date: When the crisis ended or is predicted to end
        confidence_score: Confidence score of the prediction (0-1)
        impact_score: Impact score of the crisis (0-100)
        parameters: Parameters used for prediction as JSON
        extra_data: Additional metadata as JSON
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "crisis_events"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dataset_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL")
    )
    crisis_type: Mapped[CrisisType] = mapped_column(
        Enum(CrisisType),
        default=CrisisType.OTHER,
        nullable=False
    )
    severity: Mapped[CrisisSeverity] = mapped_column(
        Enum(CrisisSeverity),
        default=CrisisSeverity.MEDIUM,
        nullable=False
    )
    status: Mapped[CrisisStatus] = mapped_column(
        Enum(CrisisStatus),
        default=CrisisStatus.PREDICATED,
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(100))
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    impact_score: Mapped[Optional[float]] = mapped_column(Float)
    parameters: Mapped[Optional[dict]] = mapped_column(Text, default={})
    extra_data: Mapped[Optional[dict]] = mapped_column(Text, default={})
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
        back_populates="crisis_events"
    )
    warnings: Mapped[List["Warning"]] = relationship(
        "Warning",
        back_populates="crisis",
        foreign_keys="Warning.crisis_id"
    )
    
    def __repr__(self) -> str:
        return f"Crisis(id={self.id}, type={self.crisis_type}, severity={self.severity}, title={self.title})"
    
    @property
    def is_active(self) -> bool:
        """Check if crisis is currently active (predicted, confirmed, or ongoing)."""
        return self.status in [CrisisStatus.PREDICATED, CrisisStatus.CONFIRMED, CrisisStatus.ONGOING]
    
    @property
    def is_high_priority(self) -> bool:
        """Check if crisis is high priority (high or critical severity)."""
        return self.severity in [CrisisSeverity.HIGH, CrisisSeverity.CRITICAL]
    
    @property
    def risk_level(self) -> str:
        """Calculate overall risk level based on severity and confidence."""
        if self.confidence_score is None or self.impact_score is None:
            return self.severity.value
        
        # Simple risk calculation: severity * confidence * impact
        severity_weight = {
            CrisisSeverity.LOW: 1,
            CrisisSeverity.MEDIUM: 2,
            CrisisSeverity.HIGH: 3,
            CrisisSeverity.CRITICAL: 4,
        }.get(self.severity, 1)
        
        risk_score = severity_weight * (self.confidence_score or 0) * (self.impact_score or 0) / 100
        
        if risk_score >= 8:
            return "critical"
        elif risk_score >= 6:
            return "high"
        elif risk_score >= 4:
            return "medium"
        elif risk_score >= 2:
            return "low"
        else:
            return "minimal"