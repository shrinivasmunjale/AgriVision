from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class DiseaseRecommendation(Base):
    __tablename__ = "disease_recommendations"
    __table_args__ = (
        UniqueConstraint("model_class", "active_ingredient", "source_url", name="uq_disease_recommendation_source"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    model_class: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    crop: Mapped[str] = mapped_column(String(50), nullable=False, default="Tomato")
    recommendation_type: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    active_ingredient: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    formulation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dose: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dose_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    water_volume: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    application_method: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    crop_stage: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    frequency: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    pre_harvest_interval: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    re_entry_period: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_organization: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    source_document: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Text, UniqueConstraint, func


class FertilizerRecommendation(Base):
    __tablename__ = "fertilizer_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    crop: Mapped[str] = mapped_column(String(100), nullable=False, default="Tomato", index=True)
    condition: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    variety_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    crop_stage: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    soil_test_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    nutrient: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nitrogen_kg_ha: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    phosphorus_kg_ha: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    potassium_kg_ha: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fym_tonne_ha: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    application_schedule: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dose: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dose_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    application_method: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    source_organization: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    source_document: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_level: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    evidence_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())



class EvidenceSource(Base):
    __tablename__ = "evidence_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    organization: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    authority_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    accessed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

