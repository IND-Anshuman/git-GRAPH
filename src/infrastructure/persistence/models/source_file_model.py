"""SQLAlchemy model for Source File."""

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.models.base import Base

class SourceFileModel(Base):
    """SQLAlchemy model representing a source code file."""
    
    __tablename__ = "source_files"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"))
    file_path: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(20))
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    line_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
