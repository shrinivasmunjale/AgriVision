from sqlalchemy import String, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

# Many-to-Many Association Tables
disease_pesticide = Table(
    "disease_pesticide",
    Base.metadata,
    Column("disease_id", Integer, ForeignKey("diseases.id", ondelete="CASCADE"), primary_key=True),
    Column("pesticide_id", Integer, ForeignKey("pesticides.id", ondelete="CASCADE"), primary_key=True),
)

disease_fertilizer = Table(
    "disease_fertilizer",
    Base.metadata,
    Column("disease_id", Integer, ForeignKey("diseases.id", ondelete="CASCADE"), primary_key=True),
    Column("fertilizer_id", Integer, ForeignKey("fertilizers.id", ondelete="CASCADE"), primary_key=True),
)

class Disease(Base):
    __tablename__ = "diseases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    symptoms: Mapped[str] = mapped_column(String(2000), nullable=False)
    causes: Mapped[str] = mapped_column(String(2000), nullable=False)
    severity_level: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "Low", "Medium", "High"
    reference_image_url: Mapped[str] = mapped_column(String(512), nullable=True)

    # Relationships
    pesticides: Mapped[list["Pesticide"]] = relationship(
        "Pesticide", secondary=disease_pesticide, back_populates="diseases"
    )
    fertilizers: Mapped[list["Fertilizer"]] = relationship(
        "Fertilizer", secondary=disease_fertilizer, back_populates="diseases"
    )
