"""SQLAlchemy model for Repository."""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructure.persistence.models.base import Base

class RepositoryModel(Base):
    """SQLAlchemy model representing a code repository."""
    
    __tablename__ = "repositories"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(Text, unique=True)
    default_branch: Mapped[str] = mapped_column(String(100))
    local_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
