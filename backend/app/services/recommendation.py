import json
import math
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from collections import Counter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.disease import Disease
from app.models.pesticide import Pesticide
from app.models.fertilizer import Fertilizer

DATA_DIR = Path(__file__).resolve().parent.parent / "db" / "data"
KNOWLEDGE_JSON_PATH = DATA_DIR / "tomato_disease_knowledge.json"
PESTICIDES_JSON_PATH = DATA_DIR / "pesticides.json"


class RecommendationEngine:
    """Enhanced recommendation engine utilizing JSON datasets in app/db/data and crop life stage filtering"""

    def __init__(self):
        self.knowledge_data: List[Dict] = []
        self.pesticides_data: List[Dict] = []
        self._load_datasets()

    def _load_datasets(self):
        """Load static datasets from app/db/data/ directory if available."""
        if KNOWLEDGE_JSON_PATH.exists():
            try:
                with open(KNOWLEDGE_JSON_PATH, "r", encoding="utf-8") as f:
                    self.knowledge_data = json.load(f)
            except Exception as e:
                print(f"[WARNING] Could not load knowledge JSON: {e}")

        if PESTICIDES_JSON_PATH.exists():
            try:
                with open(PESTICIDES_JSON_PATH, "r", encoding="utf-8") as f:
                    self.pesticides_data = json.load(f)
            except Exception as e:
                print(f"[WARNING] Could not load pesticides dataset JSON: {e}")

    @staticmethod
    def determine_life_stage(crop_age_days: Optional[int] = None, life_stage: Optional[str] = None) -> str:
        """
        Determine standardized crop life stage based on days or input string.
        Ranges:
          0 - 20 days  -> Seedling
          21 - 45 days -> Vegetative
          46 - 70 days -> Flowering
          71+ days     -> Fruiting
        """
        if life_stage and life_stage.strip():
            stage_clean = life_stage.strip().capitalize()
            valid_stages = ["Seedling", "Vegetative", "Flowering", "Fruiting"]
            for vs in valid_stages:
                if stage_clean.lower() in vs.lower():
                    return vs

        if crop_age_days is not None:
            if crop_age_days <= 20:
                return "Seedling"
            elif crop_age_days <= 45:
                return "Vegetative"
            elif crop_age_days <= 70:
                return "Flowering"
            else:
                return "Fruiting"

        return "Vegetative"  # Default fallback

    def _calculate_word_frequency(self, text: str) -> Dict[str, int]:
        """Calculate word frequency in text"""
        words = text.lower().split()
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were'
        }
        words = [w for w in words if w not in stop_words and len(w) > 2]
        return Counter(words)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        freq1 = self._calculate_word_frequency(text1)
        freq2 = self._calculate_word_frequency(text2)

        if not freq1 or not freq2:
            return 0.0

        common_words = set(freq1.keys()) & set(freq2.keys())
        if not common_words:
            return 0.0

        dot_product = sum(freq1[word] * freq2[word] for word in common_words)
        mag1 = math.sqrt(sum(freq ** 2 for freq in freq1.values()))
        mag2 = math.sqrt(sum(freq ** 2 for freq in freq2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    async def get_recommendations(
        self,
        disease_id: int,
        db: AsyncSession,
        crop_age_days: Optional[int] = None,
        life_stage: Optional[str] = None,
        top_k: int = 3
    ) -> dict:
        """
        Get top-k pesticide and fertilizer recommendations tailored to disease and crop life stage.
        """
        active_life_stage = self.determine_life_stage(crop_age_days, life_stage)

        # 1. Fetch disease from DB
        disease_result = await db.execute(
            select(Disease).filter(Disease.id == disease_id)
        )
        disease = disease_result.scalars().first()

        if not disease:
            return {"pesticides": [], "fertilizers": [], "life_stage": active_life_stage}

        disease_text = f"{disease.name} {disease.description} {disease.symptoms} {disease.causes}"

        # 2. Get all pesticides and fertilizers from DB
        pesticides_result = await db.execute(select(Pesticide))
        pesticides = pesticides_result.scalars().all()

        fertilizers_result = await db.execute(select(Fertilizer))
        fertilizers = fertilizers_result.scalars().all()

        # Build JSON pesticide lookup for life stage compatibility
        pest_stage_map = {}
        for item in self.pesticides_data:
            name_key = item.get("name", "").lower()
            pest_stage_map[name_key] = [s.lower() for s in item.get("suitable_life_stages", [])]

        # 3. Recommend pesticides with life stage boost
        pesticide_recommendations = []
        if pesticides:
            for pesticide in pesticides:
                pesticide_text = f"{pesticide.name} {pesticide.active_ingredient} {pesticide.application_method}"
                base_similarity = self._calculate_similarity(disease_text, pesticide_text)

                # Life stage compatibility multiplier
                multiplier = 1.0
                suitable_stages = pest_stage_map.get(pesticide.name.lower(), [])
                if suitable_stages:
                    if active_life_stage.lower() in suitable_stages:
                        multiplier = 1.25  # 25% boost for stage-matching treatment
                    else:
                        multiplier = 0.85  # slight penalty if not primary stage

                final_score = round(min(1.0, base_similarity * multiplier), 4)

                pesticide_recommendations.append({
                    "pesticide_id": pesticide.id,
                    "pesticide_name": pesticide.name,
                    "similarity_score": final_score,
                    "life_stage_match": active_life_stage
                })

            pesticide_recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
            pesticide_recommendations = pesticide_recommendations[:top_k]

        # 4. Recommend fertilizers with life stage match
        fertilizer_recommendations = []
        if fertilizers:
            for fertilizer in fertilizers:
                fertilizer_text = f"{fertilizer.name} {fertilizer.composition} {fertilizer.application_stage}"
                base_similarity = self._calculate_similarity(disease_text, fertilizer_text)

                # Check if fertilizer application_stage matches current active stage
                multiplier = 1.0
                if active_life_stage.lower() in fertilizer.application_stage.lower():
                    multiplier = 1.3
                elif "throughout" in fertilizer.application_stage.lower() or "all" in fertilizer.application_stage.lower():
                    multiplier = 1.1

                final_score = round(min(1.0, base_similarity * multiplier), 4)

                fertilizer_recommendations.append({
                    "fertilizer_id": fertilizer.id,
                    "fertilizer_name": fertilizer.name,
                    "similarity_score": final_score,
                    "life_stage_match": active_life_stage
                })

            fertilizer_recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
            fertilizer_recommendations = fertilizer_recommendations[:top_k]

        return {
            "pesticides": pesticide_recommendations,
            "fertilizers": fertilizer_recommendations,
            "life_stage": active_life_stage
        }

    def get_disease_knowledge(self, disease_name: Optional[str]) -> Optional[Dict]:
        """Lookup disease knowledge details from tomato_disease_knowledge.json by disease name."""
        if not disease_name or not self.knowledge_data:
            return None

        search = disease_name.lower().replace("tomato___", "").replace("tomato", "").replace("_", " ").strip()

        for entry in self.knowledge_data:
            k_name = entry.get("disease", "").lower().replace("tomato", "").strip()
            if search == k_name or search in k_name or k_name in search:
                return entry

        return None


recommendation_engine = RecommendationEngine()
