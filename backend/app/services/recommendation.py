from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Tuple, Dict
from collections import Counter
import math

from app.models.disease import Disease
from app.models.pesticide import Pesticide
from app.models.fertilizer import Fertilizer

class RecommendationEngine:
    """Simple recommendation engine without external ML dependencies"""
    
    def _calculate_word_frequency(self, text: str) -> Dict[str, int]:
        """Calculate word frequency in text"""
        words = text.lower().split()
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were'}
        words = [w for w in words if w not in stop_words and len(w) > 2]
        return Counter(words)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple cosine similarity between two texts"""
        freq1 = self._calculate_word_frequency(text1)
        freq2 = self._calculate_word_frequency(text2)
        
        if not freq1 or not freq2:
            return 0.0
        
        # Get common words
        common_words = set(freq1.keys()) & set(freq2.keys())
        
        if not common_words:
            return 0.0
        
        # Calculate dot product
        dot_product = sum(freq1[word] * freq2[word] for word in common_words)
        
        # Calculate magnitudes
        mag1 = math.sqrt(sum(freq ** 2 for freq in freq1.values()))
        mag2 = math.sqrt(sum(freq ** 2 for freq in freq2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    async def get_recommendations(
        self, 
        disease_id: int, 
        db: AsyncSession,
        top_k: int = 3
    ) -> dict:
        """
        Get top-k pesticide and fertilizer recommendations for a disease
        using simple text similarity
        """
        # Get disease info
        disease_result = await db.execute(
            select(Disease).filter(Disease.id == disease_id)
        )
        disease = disease_result.scalars().first()
        
        if not disease:
            return {"pesticides": [], "fertilizers": []}
        
        # Create disease profile text
        disease_text = f"{disease.description} {disease.symptoms} {disease.causes}"
        
        # Get all pesticides and fertilizers
        pesticides_result = await db.execute(select(Pesticide))
        pesticides = pesticides_result.scalars().all()
        
        fertilizers_result = await db.execute(select(Fertilizer))
        fertilizers = fertilizers_result.scalars().all()
        
        # Recommend pesticides
        pesticide_recommendations = []
        if pesticides:
            for pesticide in pesticides:
                pesticide_text = f"{pesticide.name} {pesticide.active_ingredient} {pesticide.application_method}"
                similarity = self._calculate_similarity(disease_text, pesticide_text)
                pesticide_recommendations.append({
                    "pesticide_id": pesticide.id,
                    "pesticide_name": pesticide.name,
                    "similarity_score": similarity
                })
            
            # Sort by similarity and get top k
            pesticide_recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
            pesticide_recommendations = pesticide_recommendations[:top_k]
        
        # Recommend fertilizers
        fertilizer_recommendations = []
        if fertilizers:
            for fertilizer in fertilizers:
                fertilizer_text = f"{fertilizer.name} {fertilizer.composition} {fertilizer.application_stage}"
                similarity = self._calculate_similarity(disease_text, fertilizer_text)
                fertilizer_recommendations.append({
                    "fertilizer_id": fertilizer.id,
                    "fertilizer_name": fertilizer.name,
                    "similarity_score": similarity
                })
            
            # Sort by similarity and get top k
            fertilizer_recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
            fertilizer_recommendations = fertilizer_recommendations[:top_k]
        
        return {
            "pesticides": pesticide_recommendations,
            "fertilizers": fertilizer_recommendations
        }

recommendation_engine = RecommendationEngine()
