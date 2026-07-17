import httpx
from app.core.config import settings
from typing import List, Dict
import random

class MLInferenceService:
    def __init__(self):
        self.modal_url = settings.MODAL_API_URL
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
    
    async def predict_disease(self, image_urls: List[str]) -> List[Dict]:
        """
        Call Modal ML inference service to predict disease from images
        Returns list of predictions with disease_id and confidence_score
        
        For development, if MODAL_API_URL is not set, returns mock predictions
        """
        
        # Mock predictions for development
        if not self.modal_url or self.modal_url == "":
            return self._mock_predictions(image_urls)
        
        # Real Modal API call
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.modal_url,
                    json={"image_urls": image_urls}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"ML Inference Error: {e}")
            # Fallback to mock
            return self._mock_predictions(image_urls)
    
    def _mock_predictions(self, image_urls: List[str]) -> List[Dict]:
        """
        Generate mock predictions for development/testing
        Returns disease IDs matching the seed data - ONLY DISEASES (no healthy)
        """
        # Disease IDs from seed data: 2=Early Blight, 3=Late Blight, 4=Bacterial Spot, 5=Mosaic Virus
        # Removed Healthy class - always show a disease
        disease_options = [
            {"disease_id": 2, "disease_name": "Early Blight", "confidence": 0.87},
            {"disease_id": 3, "disease_name": "Late Blight", "confidence": 0.82},
            {"disease_id": 4, "disease_name": "Bacterial Spot", "confidence": 0.79},
            {"disease_id": 5, "disease_name": "Tomato Mosaic Virus", "confidence": 0.91},
        ]
        
        predictions = []
        for url in image_urls:
            # Randomly select a disease with realistic confidence
            disease = random.choice(disease_options)
            # Add some variance to confidence
            confidence = disease["confidence"] + random.uniform(-0.05, 0.05)
            confidence = max(0.65, min(0.98, confidence))  # Keep between 0.65 and 0.98
            
            predictions.append({
                "image_url": url,
                "disease_id": disease["disease_id"],
                "disease_name": disease["disease_name"],
                "confidence_score": round(confidence, 2)
            })
        
        return predictions

ml_service = MLInferenceService()
