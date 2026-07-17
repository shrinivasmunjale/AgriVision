from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.disease import disease_pesticide

class Pesticide(Base):
    __tablename__ = "pesticides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active_ingredient: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str] = mapped_column(String(255), nullable=False)
    application_method: Mapped[str] = mapped_column(String(512), nullable=False)

    # Relationships
    diseases: Mapped[list["Disease"]] = relationship(
        "Disease", secondary=disease_pesticide, back_populates="pesticides"
    )
