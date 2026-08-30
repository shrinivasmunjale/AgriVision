import json
from pathlib import Path
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.disease import Disease
from app.models.fertilizer import Fertilizer

class RecommendationEngine:
    """Recommendation engine powered by pesticides.json and fertilizers catalog"""
    
    def __init__(self):
        self._pesticides_data = None
        self._load_pesticides_data()

    def _load_pesticides_data(self) -> List[Dict]:
        """Load curated pesticides catalog from pesticides.json"""
        candidate_paths = [
            Path(__file__).resolve().parent.parent / "db" / "pesticides.json",
            Path.cwd() / "backend" / "app" / "db" / "pesticides.json",
            Path.cwd() / "app" / "db" / "pesticides.json",
            Path("backend/app/db/pesticides.json"),
            Path("app/db/pesticides.json"),
        ]
        for p in candidate_paths:
            if p.exists() and p.is_file():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        self._pesticides_data = json.load(f)
                        print(f"[RECS] Loaded {len(self._pesticides_data)} disease entries from {p}")
                        return self._pesticides_data
                except Exception as err:
                    print(f"[RECS] Error parsing {p}: {err}")
        self._pesticides_data = []
        return self._pesticides_data

    def get_pesticide_products_by_disease_name(self, disease_name: str) -> Dict:
        """Fetch exact products and recommendations for a disease from pesticides.json"""
        if not self._pesticides_data:
            self._load_pesticides_data()

        clean_name = disease_name.strip().lower()
        matched_entry = None

        for entry in self._pesticides_data:
            entry_name = entry.get("disease", "").strip().lower()
            if entry_name == clean_name:
                matched_entry = entry
                break
            if clean_name in entry_name or entry_name in clean_name:
                matched_entry = entry
                break

        if not matched_entry:
            return {"products": [], "recommendation": "", "crop_stage": "All"}

        products = []
        for idx, prod in enumerate(matched_entry.get("products", []), start=1):
            priority = prod.get("priority", idx)
            score = max(0.80, round(0.98 - (priority - 1) * 0.04, 2))
            products.append({
                "pesticide_id": idx,
                "pesticide_name": prod.get("name"),
                "type": prod.get("type", "Fungicide"),
                "active_ingredient": prod.get("active_ingredient", "N/A"),
                "dosage": prod.get("dosage", "N/A"),
                "spray_interval": prod.get("spray_interval", "N/A"),
                "application_method": prod.get("application_method", "Foliar Spray"),
                "priority": priority,
                "effectiveness": prod.get("effectiveness", "High"),
                "waiting_period": prod.get("waiting_period"),
                "precautions": prod.get("precautions", []),
                "similarity_score": score,
                "crop_stage": matched_entry.get("crop_stage", "All"),
                "recommendation_note": matched_entry.get("recommendation", "")
            })

        return {
            "products": products,
            "recommendation": matched_entry.get("recommendation", ""),
            "crop_stage": matched_entry.get("crop_stage", "All")
        }

    async def get_recommendations(
        self, 
        disease_id: int, 
        db: AsyncSession,
        top_k: int = 4
    ) -> dict:
        """
        Get pesticide recommendations from pesticides.json and fertilizer recommendations
        for a detected disease
        """
        # Get disease info
        disease_result = await db.execute(
            select(Disease).filter(Disease.id == disease_id)
        )
        disease = disease_result.scalars().first()
        
        if not disease:
            return {"pesticides": [], "fertilizers": []}
        
        # 1. Pesticides directly from curated pesticides.json
        pesticide_info = self.get_pesticide_products_by_disease_name(disease.name)
        pesticide_recommendations = pesticide_info["products"][:top_k]
        
        # 2. Fertilizers from DB
        fertilizers_result = await db.execute(select(Fertilizer))
        fertilizers = fertilizers_result.scalars().all()
        
        fertilizer_recommendations = []
        if fertilizers:
            for idx, fert in enumerate(fertilizers, start=1):
                fertilizer_recommendations.append({
                    "fertilizer_id": fert.id,
                    "fertilizer_name": fert.name,
                    "composition": getattr(fert, "composition", "N/A"),
                    "dosage": getattr(fert, "dosage", "N/A"),
                    "application_stage": getattr(fert, "application_stage", "N/A"),
                    "similarity_score": max(0.85, round(0.95 - (idx - 1) * 0.05, 2))
                })
            fertilizer_recommendations = fertilizer_recommendations[:2]
        
        return {
            "pesticides": pesticide_recommendations,
            "fertilizers": fertilizer_recommendations,
            "recommendation_note": pesticide_info.get("recommendation", ""),
            "crop_stage": pesticide_info.get("crop_stage", "All")
        }

recommendation_engine = RecommendationEngine()
