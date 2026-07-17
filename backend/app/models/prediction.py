from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
from app.db.base_class import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    disease_id: Mapped[int] = mapped_column(Integer, ForeignKey("diseases.id", ondelete="SET NULL"), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User")
    disease: Mapped["Disease"] = relationship("Disease")
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="prediction", cascade="all, delete-orphan")
    report: Mapped["Report"] = relationship("Report", back_populates="prediction", uselist=False, cascade="all, delete-orphan")
