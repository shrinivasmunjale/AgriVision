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

        disease_name_clean = disease.name.lower().replace("tomato___", "").replace("tomato", "").replace("_", " ").strip()
        knowledge = self.get_disease_knowledge(disease.name)

        # 2. Get all pesticides and fertilizers from DB
        pesticides_result = await db.execute(select(Pesticide))
        pesticides = list(pesticides_result.scalars().all())

        fertilizers_result = await db.execute(select(Fertilizer))
        fertilizers = list(fertilizers_result.scalars().all())

        # Disease to specific treatment affinity heuristics
        disease_affinity = {
            "bacterial spot": {"copper": 0.94, "bacillus": 0.88, "oxychloride": 0.91},
            "early blight": {"mancozeb": 0.93, "chlorothalonil": 0.91, "azoxystrobin": 0.86, "copper": 0.82},
            "late blight": {"mancozeb": 0.95, "chlorothalonil": 0.92, "copper": 0.85, "azoxystrobin": 0.88},
            "leaf mold": {"chlorothalonil": 0.92, "copper": 0.89, "mancozeb": 0.84},
            "septoria leaf spot": {"chlorothalonil": 0.94, "mancozeb": 0.90, "copper": 0.85},
            "spider mites": {"abamectin": 0.96, "neem": 0.88},
            "two-spotted spider mite": {"abamectin": 0.96, "neem": 0.88},
            "target spot": {"azoxystrobin": 0.93, "chlorothalonil": 0.89, "mancozeb": 0.85},
            "yellow leaf curl virus": {"bacillus": 0.82, "neem": 0.86, "copper": 0.78},
            "mosaic virus": {"bacillus": 0.80, "neem": 0.78},
            "healthy": {"bacillus": 0.90, "copper": 0.75}
        }

        # Find best affinity dictionary
        target_aff = {}
        for d_key, aff_dict in disease_affinity.items():
            if d_key in disease_name_clean or disease_name_clean in d_key:
                target_aff = aff_dict
                break

        # 3. Recommend pesticides
        pesticide_recommendations = []
        if pesticides:
            for pesticide in pesticides:
                pname = pesticide.name.lower()
                # Determine base efficacy score
                base_score = 0.65
                for aff_k, aff_v in target_aff.items():
                    if aff_k in pname or aff_k in pesticide.active_ingredient.lower():
                        base_score = aff_v
                        break

                # Life stage compatibility check
                suitable_stages = []
                for p_data in self.pesticides_data:
                    if p_data.get("name", "").lower() in pname:
                        suitable_stages = [s.lower() for s in p_data.get("suitable_life_stages", [])]
                        break

                multiplier = 1.0
                if suitable_stages:
                    if active_life_stage.lower() in suitable_stages:
                        multiplier = 1.05
                    else:
                        multiplier = 0.92

                final_score = round(min(0.98, max(0.60, base_score * multiplier)), 2)

                pesticide_recommendations.append({
                    "pesticide_id": pesticide.id,
                    "pesticide_name": pesticide.name,
                    "similarity_score": final_score,
                    "life_stage_match": active_life_stage
                })

            pesticide_recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
            pesticide_recommendations = pesticide_recommendations[:top_k]

        # 4. Recommend fertilizers
        fertilizer_recommendations = []
        if fertilizers:
            for fertilizer in fertilizers:
                fname = fertilizer.name.lower()
                fstage = (fertilizer.application_stage or "").lower()
                base_score = 0.75

                if "npk" in fname or "balanced" in fname:
                    base_score = 0.90
                elif "calcium" in fname:
                    base_score = 0.88 if active_life_stage.lower() in ["flowering", "fruiting"] else 0.82
                elif "potassium" in fname or "sulfate" in fname or "boost" in fname:
                    base_score = 0.86

                multiplier = 1.0
                if active_life_stage.lower() in fstage:
                    multiplier = 1.08
                elif "all" in fstage or "throughout" in fstage:
                    multiplier = 1.02

                final_score = round(min(0.96, max(0.65, base_score * multiplier)), 2)

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
