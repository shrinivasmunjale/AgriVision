from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base_class import Base

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    prediction_id: Mapped[str] = mapped_column(String(36), ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False)
    file_url: Mapped[str] = mapped_column(String(512), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    prediction: Mapped["Prediction"] = relationship("Prediction", back_populates="report")
