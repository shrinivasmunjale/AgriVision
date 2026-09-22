from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.evidence_recommendation import FertilizerRecommendation

router = APIRouter()

DEFAULT_DISCLAIMER = (
    "Reference guidance: This recommendation is based on an MPKV research reference. "
    "Actual fertilizer requirements may vary according to soil condition, crop stage, variety, "
    "previous crop, irrigation and local agricultural guidance. Follow current agricultural "
    "recommendations and product instructions before application."
)


def format_application_schedule(schedule_text: Optional[str]) -> Dict[str, List[str]]:
    if not schedule_text:
        return {
            "transplanting": [
                "Full FYM",
                "50% nitrogen",
                "Full phosphorus",
                "Full potassium",
            ],
            "later_applications": [
                "Remaining 50% nitrogen in 3 equal split applications at 20-day intervals",
            ],
        }

    return {
        "transplanting": [
            "Full FYM",
            "50% nitrogen",
            "Full phosphorus",
            "Full potassium",
        ],
        "later_applications": [
            "Remaining 50% nitrogen",
            "3 equal split applications",
            "20-day intervals",
        ],
    }


def serialize_fertilizer_rec(rec: FertilizerRecommendation) -> Dict[str, Any]:
    return {
        "id": rec.id,
        "crop": rec.crop,
        "variety_type": rec.variety_type,
        "crop_stage": rec.crop_stage or "Transplanting",
        "recommendation_type": "Reference",
        "soil_test_required": rec.soil_test_required,
        "nutrients": {
            "nitrogen": {
                "value": rec.nitrogen_kg_ha,
                "unit": "kg/ha",
                "display": f"{rec.nitrogen_kg_ha} kg/ha" if rec.nitrogen_kg_ha else None,
            },
            "phosphorus": {
                "value": rec.phosphorus_kg_ha,
                "unit": "kg/ha",
                "display": f"{rec.phosphorus_kg_ha} kg/ha (P₂O₅)" if rec.phosphorus_kg_ha else None,
            },
            "potassium": {
                "value": rec.potassium_kg_ha,
                "unit": "kg/ha",
                "display": f"{rec.potassium_kg_ha} kg/ha (K₂O)" if rec.potassium_kg_ha else None,
            },
            "fym": {
                "value": rec.fym_tonne_ha,
                "unit": "tonnes/ha",
                "display": f"{rec.fym_tonne_ha} tonnes/ha" if rec.fym_tonne_ha else None,
            },
        },
        "application_schedule": format_application_schedule(rec.application_schedule),
        "application_method": rec.application_method or "Basal application and top dressing splits",
        "source": {
            "organization": rec.source_organization or "Mahatma Phule Krishi Vidyapeeth (MPKV), Rahuri",
            "source_type": rec.source_type or "Agricultural University Research Recommendation",
            "document": rec.source_document or "AICRP on Vegetables - Research Recommendations",
            "url": rec.source_url or "https://mpkv.ac.in/Uploads/Research/33.%20AICRP%20on%20Vegetables_20250926041136.pdf",
            "evidence_level": rec.evidence_level or "AGRICULTURAL_UNIVERSITY",
            "evidence_note": rec.evidence_note,
            "verified_date": str(rec.verified_date) if rec.verified_date else None,
        },
        "disclaimer": DEFAULT_DISCLAIMER,
    }


@router.get("")
async def get_fertilizer_recommendations(
    crop: str = Query("Tomato", description="Crop name"),
    variety_type: Optional[str] = Query(None, description="Hybrid, Improved Variety, or unknown"),
    crop_stage: Optional[str] = Query(None, description="Crop stage"),
    soil_test_available: Optional[bool] = Query(False, description="Whether soil test is available"),
    db: AsyncSession = Depends(get_db),
):
    normalized_crop = crop.strip().capitalize() if crop else "Tomato"
    normalized_variety = variety_type.strip() if variety_type else None

    # Handle "I don't know" or unknown variety
    if normalized_variety and normalized_variety.lower() in ["i don't know", "dont know", "unknown", "none", ""]:
        normalized_variety = None

    # Query DB for matching fertilizer recommendations
    stmt = select(FertilizerRecommendation).where(
        FertilizerRecommendation.crop.ilike(f"%{normalized_crop}%"),
        FertilizerRecommendation.is_active.is_(True),
    )

    if normalized_variety:
        stmt = stmt.where(FertilizerRecommendation.variety_type.ilike(f"%{normalized_variety}%"))

    stmt = stmt.order_by(FertilizerRecommendation.id)
    result = await db.execute(stmt)
    records = result.scalars().all()

    if not records:
        # If farmer selected "I don't know" or no record matched variety
        if not normalized_variety:
            # Return general reference note without guessing Hybrid
            return {
                "crop": normalized_crop,
                "variety_type": "Not Specified",
                "recommendation_type": "General Reference",
                "recommendations": [],
                "message": (
                    "A variety-specific fertilizer recommendation is not available without variety information. "
                    "For Tomato, MPKV Rahuri provides distinct recommendations for Hybrid (300:150:150 kg/ha NPK) "
                    "and Improved Varieties (200:100:100 kg/ha NPK). Please select your variety if known."
                ),
                "disclaimer": DEFAULT_DISCLAIMER,
            }
        return {
            "crop": normalized_crop,
            "variety_type": normalized_variety,
            "recommendations": [],
            "message": f"No locally verified fertilizer recommendation found for {normalized_crop} ({normalized_variety}).",
            "disclaimer": DEFAULT_DISCLAIMER,
        }

    serialized_list = [serialize_fertilizer_rec(r) for r in records]
    primary_rec = serialized_list[0]

    response_data = {
        **primary_rec,
        "all_recommendations": serialized_list,
        "soil_test_note": (
            "Soil-test-based personalization can be added using validated soil-testing laboratory parameters."
            if soil_test_available
            else "Standard research reference used. Soil test report not required for basic guidance."
        ),
    }

    return response_data
