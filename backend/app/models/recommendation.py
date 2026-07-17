from sqlalchemy import Integer, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    prediction_id: Mapped[str] = mapped_column(String(36), ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False)
    pesticide_id: Mapped[int] = mapped_column(Integer, ForeignKey("pesticides.id", ondelete="SET NULL"), nullable=True)
    fertilizer_id: Mapped[int] = mapped_column(Integer, ForeignKey("fertilizers.id", ondelete="SET NULL"), nullable=True)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    prediction: Mapped["Prediction"] = relationship("Prediction", back_populates="recommendations")
    pesticide: Mapped["Pesticide"] = relationship("Pesticide")
    fertilizer: Mapped["Fertilizer"] = relationship("Fertilizer")
