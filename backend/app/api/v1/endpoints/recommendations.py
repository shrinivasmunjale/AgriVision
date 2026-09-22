from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.db.session import get_db
from app.models.evidence_recommendation import DiseaseRecommendation

router = APIRouter()

EXACT_MODEL_CLASSES = {
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
}

MODEL_CLASS_BY_NAME = {
    "bacterial spot": "Tomato___Bacterial_spot",
    "tomato bacterial spot": "Tomato___Bacterial_spot",
    "early blight": "Tomato___Early_blight",
    "tomato early blight": "Tomato___Early_blight",
    "late blight": "Tomato___Late_blight",
    "tomato late blight": "Tomato___Late_blight",
    "leaf mold": "Tomato___Leaf_Mold",
    "tomato leaf mold": "Tomato___Leaf_Mold",
    "septoria leaf spot": "Tomato___Septoria_leaf_spot",
    "tomato septoria leaf spot": "Tomato___Septoria_leaf_spot",
    "spider mites": "Tomato___Spider_mites Two-spotted_spider_mite",
    "spider mites (two-spotted)": "Tomato___Spider_mites Two-spotted_spider_mite",
    "spider mites two-spotted spider mite": "Tomato___Spider_mites Two-spotted_spider_mite",
    "two-spotted spider mite": "Tomato___Spider_mites Two-spotted_spider_mite",
    "two spotted spider mite": "Tomato___Spider_mites Two-spotted_spider_mite",
    "tomato spider mites": "Tomato___Spider_mites Two-spotted_spider_mite",
    "tomato spider mites (two-spotted)": "Tomato___Spider_mites Two-spotted_spider_mite",
    "tomato spider mites two-spotted spider mite": "Tomato___Spider_mites Two-spotted_spider_mite",
    "target spot": "Tomato___Target_Spot",
    "tomato target spot": "Tomato___Target_Spot",
    "tomato yellow leaf curl virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "tomato tomato yellow leaf curl virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "yellow leaf curl virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "tylcv": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "tomato mosaic virus": "Tomato___Tomato_mosaic_virus",
    "tomato tomato mosaic virus": "Tomato___Tomato_mosaic_virus",
    "tomv": "Tomato___Tomato_mosaic_virus",
    "mosaic virus": "Tomato___Tomato_mosaic_virus",
    "healthy": "Tomato___healthy",
    "tomato healthy": "Tomato___healthy",
}


def model_class_for_name(disease_name: str | None) -> str | None:
    if not disease_name:
        return None
    if disease_name in EXACT_MODEL_CLASSES:
        return disease_name
    normalized = disease_name.lower().replace("tomato___", "").replace("_", " ").strip()
    if normalized in MODEL_CLASS_BY_NAME:
        return MODEL_CLASS_BY_NAME[normalized]
    # Remove leading 'tomato ' if present
    if normalized.startswith("tomato "):
        trimmed = normalized[7:].strip()
        if trimmed in MODEL_CLASS_BY_NAME:
            return MODEL_CLASS_BY_NAME[trimmed]
    # Try partial matching across keys
    for key, model_cls in MODEL_CLASS_BY_NAME.items():
        if key in normalized or normalized in key:
            return model_cls
    return None


def serialize_recommendation(record: DiseaseRecommendation) -> dict:
    return {
        "id": record.id,
        "type": record.recommendation_type,
        "active_ingredient": record.active_ingredient,
        "formulation": record.formulation,
        "dose": record.dose,
        "dose_unit": record.dose_unit,
        "water_volume": record.water_volume,
        "application_method": record.application_method,
        "crop_stage": record.crop_stage,
        "frequency": record.frequency,
        "pre_harvest_interval": record.pre_harvest_interval,
        "re_entry_period": record.re_entry_period,
        "source": {
            "organization": record.source_organization,
            "source_type": record.source_type,
            "document": record.source_document,
            "url": record.source_url,
            "evidence_note": record.evidence_note,
            "verified_date": str(record.verified_date) if record.verified_date else None,
        },
    }


def serialize_static_record(idx: int, values: dict) -> dict:
    return {
        "id": idx,
        "type": values.get("recommendation_type"),
        "active_ingredient": values.get("active_ingredient"),
        "formulation": values.get("formulation"),
        "dose": values.get("dose"),
        "dose_unit": values.get("dose_unit"),
        "water_volume": values.get("water_volume"),
        "application_method": values.get("application_method"),
        "crop_stage": values.get("crop_stage"),
        "frequency": values.get("frequency"),
        "pre_harvest_interval": values.get("pre_harvest_interval"),
        "re_entry_period": values.get("re_entry_period"),
        "source": {
            "organization": values.get("source_organization"),
            "source_type": values.get("source_type"),
            "document": values.get("source_document"),
            "url": values.get("source_url"),
            "evidence_note": values.get("evidence_note"),
            "verified_date": str(values.get("verified_date")) if values.get("verified_date") else None,
        },
    }


async def get_evidence_recommendations(model_class: str | None, db: Optional[AsyncSession] = None) -> list[dict]:
    if not model_class:
        return []

    records = []
    if db is not None:
        try:
            result = await db.execute(
                select(DiseaseRecommendation)
                .where(
                    DiseaseRecommendation.model_class == model_class,
                    DiseaseRecommendation.is_active.is_(True),
                )
                .order_by(DiseaseRecommendation.id)
            )
            records = [serialize_recommendation(record) for record in result.scalars().all()]
        except Exception as db_err:
            print(f"[WARNING] Database error querying DiseaseRecommendation: {db_err}")
            records = []

    # If database returned 0 rows (e.g. cold start, delayed migration), use in-memory curated knowledge
    if not records:
        try:
            from seed_evidence import RECORDS
            fallback_records = [
                serialize_static_record(idx + 1, r)
                for idx, r in enumerate(RECORDS)
                if r.get("model_class") == model_class
            ]
            if fallback_records:
                return fallback_records
        except Exception as static_err:
            print(f"[WARNING] Static fallback error: {static_err}")

    return records


@router.get("/{model_class}")
async def get_recommendations(
    model_class: str,
    db: AsyncSession = Depends(get_db),
):
    resolved_class = model_class if model_class in EXACT_MODEL_CLASSES else model_class_for_name(model_class)
    if not resolved_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown EfficientNet model class or disease name",
        )

    recommendations = await get_evidence_recommendations(resolved_class, db)
    display_name = resolved_class.split("___", 1)[-1].replace("_", " ")

    return {
        "model_class": resolved_class,
        "display_name": display_name,
        "recommendations": recommendations,
        "message": None if recommendations else "No verified recommendation is currently available in the database.",
    }
