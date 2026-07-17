from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base_class import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id: Mapped[str] = mapped_column(String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False) # e.g. "CREATE_DISEASE", "UPDATE_PESTICIDE"
    entity: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "disease", "pesticide", "fertilizer"
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    admin: Mapped["User"] = relationship("User")
