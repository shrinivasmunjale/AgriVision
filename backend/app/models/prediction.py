from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List, Any
import uuid
from app.db.base_class import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    disease_id: Mapped[int] = mapped_column(Integer, ForeignKey("diseases.id", ondelete="SET NULL"), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    bounding_boxes: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    crop_age_days: Mapped[int] = mapped_column(Integer, nullable=True)
    life_stage: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User")
    disease: Mapped["Disease"] = relationship("Disease")
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="prediction", cascade="all, delete-orphan")
    report: Mapped["Report"] = relationship("Report", back_populates="prediction", uselist=False, cascade="all, delete-orphan")
