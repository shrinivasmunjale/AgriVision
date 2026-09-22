import asyncio
from datetime import date

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.evidence_recommendation import (
    DiseaseRecommendation,
    FertilizerRecommendation,
    EvidenceSource,
)


RECORDS = [
    {
        "model_class": "Tomato___Bacterial_spot",
        "display_name": "Bacterial Spot",
        "recommendation_type": "Disease management",
        "active_ingredient": "Streptocycline",
        "dose": "40-100",
        "dose_unit": "ppm",
        "application_method": "As specified in the agricultural recommendation",
        "source_organization": "TNAU",
        "source_type": "Agricultural University",
        "source_document": "TNAU Tomato Bacterial Leaf Spot Management",
        "source_url": "https://agritech.tnau.ac.in/crop_protection/tomato_diseases_11.html",
        "evidence_note": "TNAU recommends disease-free seed and lists Streptocycline 40-100 ppm for bacterial leaf spot management.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___Early_blight",
        "display_name": "Early Blight",
        "recommendation_type": "Fungicide",
        "active_ingredient": "Copper Oxychloride",
        "dose": "3",
        "dose_unit": "g/L",
        "application_method": "Foliar spray",
        "source_organization": "ICAR",
        "source_type": "Government Agricultural Advisory",
        "source_document": "ICAR Kharif Agro-Advisory 2025",
        "source_url": "https://www.icar.gov.in/sites/default/files/2025-10/ICAR-En-Kharif-Agro-Advisories-for-Farmers-2025.pdf",
        "evidence_note": "ICAR advisory lists Copper Oxychloride at 3 g/L for management of early blight and fruit rot of tomato.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___Early_blight",
        "display_name": "Early Blight",
        "recommendation_type": "Fungicide",
        "active_ingredient": "Azoxystrobin + Mancozeb",
        "formulation": "11.5% + 30% WP",
        "dose": "750-875",
        "dose_unit": "g/ha",
        "water_volume": "500 L/ha",
        "application_method": "Foliar application",
        "crop_stage": "Vegetative stage and fruiting",
        "frequency": "2-3 sprays at 10-15 day intervals",
        "pre_harvest_interval": "3 days",
        "re_entry_period": "24 hours",
        "source_organization": "PPQS",
        "source_type": "Government Pesticide Label",
        "source_document": "Azoxystrobin 11.5% + Mancozeb 30% WP Primary Package Label",
        "source_url": "https://ppqs.gov.in/sites/default/files/azoxystrobin_11.5_mancozeb_30_wp93fcrystal_crop_protection_ltd_1-merged.pdf",
        "evidence_note": "Official PPQS label specifies this formulation for early and late blight of tomato.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___Late_blight",
        "display_name": "Late Blight",
        "recommendation_type": "Fungicide",
        "active_ingredient": "Cyazofamid",
        "formulation": "34.5% SC",
        "dose": "80",
        "dose_unit": "ml/acre",
        "application_method": "Foliar spray",
        "source_organization": "TNAU",
        "source_type": "Agricultural University",
        "source_document": "TNAU Tomato Late Blight Management",
        "source_url": "https://agritech.tnau.ac.in/crop_protection/tomato_diseases_8.html",
        "evidence_note": "TNAU lists Cyazofamid 34.5% SC at 80 ml/acre for late blight.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___Late_blight",
        "display_name": "Late Blight",
        "recommendation_type": "Fungicide",
        "active_ingredient": "Azoxystrobin + Mancozeb",
        "formulation": "11.5% + 30% WP",
        "dose": "750-875",
        "dose_unit": "g/ha",
        "water_volume": "500 L/ha",
        "application_method": "Foliar application",
        "crop_stage": "Vegetative stage and fruiting",
        "frequency": "2-3 sprays at 10-15 day intervals",
        "pre_harvest_interval": "3 days",
        "re_entry_period": "24 hours",
        "source_organization": "PPQS",
        "source_type": "Government Pesticide Label",
        "source_document": "Azoxystrobin 11.5% + Mancozeb 30% WP Primary Package Label",
        "source_url": "https://ppqs.gov.in/sites/default/files/azoxystrobin_11.5_mancozeb_30_wp93fcrystal_crop_protection_ltd_1-merged.pdf",
        "evidence_note": "Official PPQS label specifies this formulation for early and late blight of tomato.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___Target_Spot",
        "display_name": "Target Spot",
        "recommendation_type": "Fungicide",
        "active_ingredient": "Mancozeb",
        "application_method": "Foliar spray",
        "source_organization": "Pacific Pests, Pathogens & Weeds",
        "source_type": "International Extension",
        "source_document": "Tomato Target Spot",
        "source_url": "https://apps.lucidcentral.org/ppp_v9/text/web_mini/entities/tomato_target_spot_163.htm",
        "evidence_note": "International extension resource identifies mancozeb as an option. No Indian dose is supplied.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "display_name": "Tomato Yellow Leaf Curl Virus",
        "recommendation_type": "IPM / Vector Management",
        "source_organization": "ICAR-IIHR",
        "source_type": "Research Institute IPM",
        "source_document": "IPM Practices for Tomato Pests",
        "source_url": "https://api-dev.iihr.res.in/ipm-practices-tomato-pests",
        "evidence_note": "Manage whitefly vectors and remove severely affected plants; the virus is not presented as cured by a fungicide.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___Tomato_mosaic_virus",
        "display_name": "Tomato Mosaic Virus",
        "recommendation_type": "Sanitation / Disease Management",
        "source_organization": "TNAU",
        "source_type": "Agricultural University",
        "source_document": "TNAU Tomato Crop Protection",
        "source_url": "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop%20diseases_veg_tomato.html",
        "evidence_note": "Use sanitation, healthy planting material and removal of infected plants. Do not present a fungicide as a cure for a viral disease.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___healthy",
        "display_name": "Healthy",
        "recommendation_type": "Monitoring",
        "evidence_note": "No pesticide recommendation. Continue crop monitoring and use crop-specific nutrient management.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___Leaf_Mold",
        "display_name": "Leaf Mold",
        "recommendation_type": "Fungicide",
        "active_ingredient": "Copper hydroxide",
        "formulation": "77% WP",
        "dose": "2",
        "dose_unit": "g/L",
        "application_method": "Foliar spray",
        "source_organization": "MANAGE",
        "source_type": "Indian Agricultural Extension Publication",
        "source_document": "Green Technologies for Sustainable Management - Diseases under Protected Environment in India",
        "source_url": "https://www.manage.gov.in/publications/eBooks/Green%20Technologies%20for%20Sustainable%20Management.pdf",
        "evidence_note": "MANAGE lists Copper hydroxide 77% WP at 2 g/L for tomato leaf mold under protected cultivation.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___Leaf_Mold",
        "display_name": "Leaf Mold",
        "recommendation_type": "Fungicide",
        "active_ingredient": "Mancozeb",
        "formulation": "75% WP",
        "dose": "2",
        "dose_unit": "g/L",
        "application_method": "Foliar spray",
        "source_organization": "MANAGE",
        "source_type": "Indian Agricultural Extension Publication",
        "source_document": "Green Technologies for Sustainable Management - Diseases under Protected Environment in India",
        "source_url": "https://www.manage.gov.in/publications/eBooks/Green%20Technologies%20for%20Sustainable%20Management.pdf",
        "evidence_note": "MANAGE lists Mancozeb 75% WP at 2 g/L for tomato leaf mold under protected cultivation.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___Leaf_Mold",
        "display_name": "Leaf Mold",
        "recommendation_type": "Fungicide",
        "active_ingredient": "Chlorothalonil",
        "formulation": "75% WP",
        "dose": "2",
        "dose_unit": "g/L",
        "application_method": "Foliar spray",
        "source_organization": "MANAGE",
        "source_type": "Indian Agricultural Extension Publication",
        "source_document": "Green Technologies for Sustainable Management - Diseases under Protected Environment in India",
        "source_url": "https://www.manage.gov.in/publications/eBooks/Green%20Technologies%20for%20Sustainable%20Management.pdf",
        "evidence_note": "MANAGE lists Chlorothalonil 75% WP at 2 g/L for tomato leaf mold under protected cultivation.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___Septoria_leaf_spot",
        "display_name": "Septoria Leaf Spot",
        "recommendation_type": "Fungicide",
        "active_ingredient": "Fluxapyroxad + Pyraclostrobin",
        "formulation": "250 g/L + 250 g/L SC",
        "dose": "200-250",
        "dose_unit": "ml/ha",
        "application_method": "Foliar application",
        "source_organization": "TNAU",
        "source_type": "Agricultural University",
        "source_document": "TNAU Crop Protection - Septoria Leaf Spot",
        "source_url": "https://agritech.tnau.ac.in/crop_protection/tomato_diseases_4.html",
        "evidence_note": "TNAU lists Fluxapyroxad 250 g/L + Pyraclostrobin 250 g/L SC at 200-250 ml/ha.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "model_class": "Tomato___Spider_mites Two-spotted_spider_mite",
        "display_name": "Two-Spotted Spider Mite",
        "recommendation_type": "Acaricide / IPM",
        "active_ingredient": "Sulphur",
        "formulation": "80 WP",
        "dose": "3",
        "dose_unit": "g/L",
        "application_method": "Foliar spray, targeting lower leaf surface",
        "source_organization": "ICAR-IIHR",
        "source_type": "Research Institute IPM",
        "source_document": "IPM Practices for Tomato Pests",
        "source_url": "https://api-dev.iihr.res.in/ipm-practices-tomato-pests",
        "evidence_note": "ICAR-IIHR lists sulphur 80 WP at 3 g/L among options when red spider mite incidence is observed.",
        "verified_date": date(2026, 9, 22),
    },
]


from app.models.evidence_recommendation import DiseaseRecommendation, FertilizerRecommendation, EvidenceSource


EVIDENCE_SOURCES = [
    {
        "organization": "ICAR-NRCIPM",
        "source_type": "Government/ICAR",
        "title": "Insecticide and Fungicide Calculators for Tomato",
        "url": "https://icar.gov.in/hi/node/10817",
        "country": "India",
        "authority_level": "National Government",
        "notes": "Pesticide and fungicide calculator and official label-claim recommendations for tomato.",
    },
    {
        "organization": "ICAR",
        "source_type": "Government Agricultural Advisory",
        "title": "ICAR Kharif Agro-Advisory 2025",
        "url": "https://www.icar.gov.in/sites/default/files/2025-10/ICAR-En-Kharif-Agro-Advisories-for-Farmers-2025.pdf",
        "country": "India",
        "authority_level": "National Government Advisory",
        "notes": "Official crop and disease advisories published by ICAR for tomato cultivation.",
    },
    {
        "organization": "PPQS",
        "source_type": "Government Pesticide Label",
        "title": "Azoxystrobin 11.5% + Mancozeb 30% WP Primary Package Label",
        "url": "https://ppqs.gov.in/sites/default/files/azoxystrobin_11.5_mancozeb_30_wp93fcrystal_crop_protection_ltd_1-merged.pdf",
        "country": "India",
        "authority_level": "Statutory Regulatory Label",
        "notes": "Directorate of Plant Protection, Quarantine & Storage registered label claims.",
    },
    {
        "organization": "TNAU",
        "source_type": "Agricultural University",
        "title": "TNAU Agritech Portal - Tomato Crop Protection",
        "url": "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop%20diseases_veg_tomato.html",
        "country": "India",
        "authority_level": "State Agricultural University",
        "notes": "Comprehensive tomato disease and pest management guidelines from Tamil Nadu Agricultural University.",
    },
    {
        "organization": "MANAGE",
        "source_type": "Indian Agricultural Extension Publication",
        "title": "Green Technologies for Sustainable Management - Diseases under Protected Environment in India",
        "url": "https://www.manage.gov.in/publications/eBooks/Green%20Technologies%20for%20Sustainable%20Management.pdf",
        "country": "India",
        "authority_level": "National Extension Institute",
        "notes": "National Institute of Agricultural Extension Management protected cultivation guide.",
    },
    {
        "organization": "ICAR-IIHR",
        "source_type": "Research Institute IPM",
        "title": "IPM Practices for Tomato Pests",
        "url": "https://api-dev.iihr.res.in/ipm-practices-tomato-pests",
        "country": "India",
        "authority_level": "ICAR Research Institute",
        "notes": "Integrated pest and vector management recommendations from ICAR-Indian Institute of Horticultural Research.",
    },
    {
        "organization": "Pacific Pests, Pathogens & Weeds",
        "source_type": "International Agricultural Extension",
        "title": "Tomato Target Spot Fact Sheet",
        "url": "https://apps.lucidcentral.org/ppp_v9/text/web_mini/entities/tomato_target_spot_163.htm",
        "country": "International",
        "authority_level": "International Extension",
        "notes": "International diagnostic and management reference for Corynespora target spot.",
    },
]

FERTILIZER_RECORDS = [
    {
        "crop": "Tomato",
        "variety_type": "Hybrid",
        "crop_stage": "Transplanting",
        "soil_test_required": False,
        "nitrogen_kg_ha": 300.0,
        "phosphorus_kg_ha": 150.0,
        "potassium_kg_ha": 150.0,
        "fym_tonne_ha": 20.0,
        "recommendation": "Apply FYM @ 20 t/ha and N:P₂O₅:K₂O @ 300:150:150 kg/ha for hybrid tomato.",
        "application_schedule": "Full FYM + 50% N + full P + full K at transplanting. Remaining 50% N in 3 equal split applications at 20-day intervals.",
        "application_method": "Basal application at transplanting and top dressing in 3 splits",
        "source_organization": "Mahatma Phule Krishi Vidyapeeth (MPKV), Rahuri",
        "source_type": "Agricultural University Research Recommendation",
        "source_document": "AICRP on Vegetables - Research Recommendations",
        "source_url": "https://mpkv.ac.in/Uploads/Research/33.%20AICRP%20on%20Vegetables_20250926041136.pdf",
        "evidence_level": "AGRICULTURAL_UNIVERSITY",
        "evidence_note": "MPKV Rahuri AICRP on Vegetables official research recommendation for hybrid tomato.",
        "verified_date": date(2026, 9, 22),
    },
    {
        "crop": "Tomato",
        "variety_type": "Improved Variety",
        "crop_stage": "Transplanting",
        "soil_test_required": False,
        "nitrogen_kg_ha": 200.0,
        "phosphorus_kg_ha": 100.0,
        "potassium_kg_ha": 100.0,
        "fym_tonne_ha": 20.0,
        "recommendation": "Apply FYM @ 20 t/ha and N:P₂O₅:K₂O @ 200:100:100 kg/ha for improved variety tomato.",
        "application_schedule": "Full FYM + 50% N + full P + full K at transplanting. Remaining 50% N in 3 equal split applications at 20-day intervals.",
        "application_method": "Basal application at transplanting and top dressing in 3 splits",
        "source_organization": "Mahatma Phule Krishi Vidyapeeth (MPKV), Rahuri",
        "source_type": "Agricultural University Research Recommendation",
        "source_document": "AICRP on Vegetables - Research Recommendations",
        "source_url": "https://mpkv.ac.in/Uploads/Research/33.%20AICRP%20on%20Vegetables_20250926041136.pdf",
        "evidence_level": "AGRICULTURAL_UNIVERSITY",
        "evidence_note": "MPKV Rahuri AICRP on Vegetables official research recommendation for improved variety tomato.",
        "verified_date": date(2026, 9, 22),
    },
]


async def seed_evidence():
    async with SessionLocal() as db:
        # 1. Seed Disease Recommendations
        seeded_disease = 0
        for values in RECORDS:
            exists = await db.execute(
                select(DiseaseRecommendation.id).where(
                    DiseaseRecommendation.model_class == values["model_class"],
                    DiseaseRecommendation.active_ingredient == values.get("active_ingredient"),
                    DiseaseRecommendation.source_url == values.get("source_url"),
                )
            )
            if exists.scalar_one_or_none() is None:
                db.add(DiseaseRecommendation(**values))
                seeded_disease += 1

        # 2. Seed Evidence Sources
        seeded_sources = 0
        for values in EVIDENCE_SOURCES:
            exists = await db.execute(
                select(EvidenceSource.id).where(
                    EvidenceSource.organization == values["organization"],
                    EvidenceSource.url == values["url"],
                )
            )
            if exists.scalar_one_or_none() is None:
                db.add(EvidenceSource(**values))
                seeded_sources += 1

        # 3. Seed Fertilizer Recommendations
        seeded_fert = 0
        for values in FERTILIZER_RECORDS:
            exists = await db.execute(
                select(FertilizerRecommendation.id).where(
                    FertilizerRecommendation.crop == values["crop"],
                    FertilizerRecommendation.variety_type == values.get("variety_type"),
                    FertilizerRecommendation.source_url == values.get("source_url"),
                )
            )
            if exists.scalar_one_or_none() is None:
                db.add(FertilizerRecommendation(**values))
                seeded_fert += 1

        await db.commit()
        print(f"Seeded: {seeded_disease} new disease recs, {seeded_sources} new sources, {seeded_fert} new fertilizer recs.")


if __name__ == "__main__":
    asyncio.run(seed_evidence())