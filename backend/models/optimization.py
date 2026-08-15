"""
Optimization record model — SQLAlchemy ORM.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class OptimizationRecord(Base):
    __tablename__ = "optimizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    resume_text: Mapped[str] = mapped_column(Text, nullable=True)
    jd_text: Mapped[str] = mapped_column(Text, nullable=True)
    section_type: Mapped[str] = mapped_column(String(50), nullable=False)
    section_content: Mapped[str] = mapped_column(Text, nullable=True)
    optimized_text: Mapped[str] = mapped_column(Text, nullable=True)
    changes_summary: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array
    match_score: Mapped[float] = mapped_column(Float, nullable=True)
    model_used: Mapped[str] = mapped_column(String(100), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict:
        import json
        return {
            "id": self.id,
            "user_id": self.user_id,
            "section_type": self.section_type,
            "optimized_text": self.optimized_text,
            "changes_summary": json.loads(self.changes_summary) if self.changes_summary else [],
            "match_score": self.match_score,
            "model_used": self.model_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }