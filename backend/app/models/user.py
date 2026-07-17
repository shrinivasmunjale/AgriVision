from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import uuid
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)  # For local auth
    role: Mapped[str] = mapped_column(String(50), default="farmer") # "farmer", "admin", or "expert"
    farm_name: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
