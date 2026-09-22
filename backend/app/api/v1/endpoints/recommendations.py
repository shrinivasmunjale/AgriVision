from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.evidence_recommendation import DiseaseRecommendation
from app.models.user import User

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
    "early blight": "Tomato___Early_blight",
    "late blight": "Tomato___Late_blight",
    "leaf mold": "Tomato___Leaf_Mold",
    "septoria leaf spot": "Tomato___Septoria_leaf_spot",
    "spider mites (two-spotted)": "Tomato___Spider_mites Two-spotted_spider_mite",
    "two-spotted spider mite": "Tomato___Spider_mites Two-spotted_spider_mite",
    "target spot": "Tomato___Target_Spot",
    "tomato yellow leaf curl virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "tomato mosaic virus": "Tomato___Tomato_mosaic_virus",
    "healthy": "Tomato___healthy",
}


def model_class_for_name(disease_name: str | None) -> str | None:
    if not disease_name:
        return None
    normalized = disease_name.lower().replace("tomato___", "").replace("_", " ").strip()
    return MODEL_CLASS_BY_NAME.get(normalized)


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
            "verified_date": record.verified_date,
        },
    }


async def get_evidence_recommendations(model_class: str | None, db: AsyncSession) -> list[dict]:
    if not model_class:
        return []
    result = await db.execute(
        select(DiseaseRecommendation)
        .where(
            DiseaseRecommendation.model_class == model_class,
            DiseaseRecommendation.is_active.is_(True),
        )
        .order_by(DiseaseRecommendation.id)
    )
    return [serialize_recommendation(record) for record in result.scalars().all()]


@router.get("/{model_class}")
async def get_recommendations(
    model_class: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if model_class not in EXACT_MODEL_CLASSES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown EfficientNet model class",
        )

    result = await db.execute(
        select(DiseaseRecommendation)
        .where(
            DiseaseRecommendation.model_class == model_class,
            DiseaseRecommendation.is_active.is_(True),
        )
        .order_by(DiseaseRecommendation.id)
    )
    records = result.scalars().all()
    display_name = records[0].display_name if records else model_class.split("___", 1)[-1].replace("_", " ")

    return {
        "model_class": model_class,
        "display_name": display_name,
        "recommendations": [serialize_recommendation(record) for record in records],
        "message": None if records else "No verified recommendation is currently available in the database.",
    }
