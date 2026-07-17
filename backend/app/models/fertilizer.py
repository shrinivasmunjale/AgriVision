from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.disease import disease_fertilizer

class Fertilizer(Base):
    __tablename__ = "fertilizers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    composition: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str] = mapped_column(String(255), nullable=False)
    application_stage: Mapped[str] = mapped_column(String(512), nullable=False)

    # Relationships
    diseases: Mapped[list["Disease"]] = relationship(
        "Disease", secondary=disease_fertilizer, back_populates="fertilizers"
    )
