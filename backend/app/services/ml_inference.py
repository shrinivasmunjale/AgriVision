import httpx
from app.core.config import settings
from app.ml.model_loader import pytorch_model_loader
from typing import List, Dict
import random

class MLInferenceService:
    def __init__(self):
        self.modal_url = settings.MODAL_API_URL
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
    
    async def predict_disease(self, image_urls: List[str]) -> List[Dict]:
        """
        Predict disease from images. Order of priority:
        1. Local custom PyTorch model (if model file exists in backend/app/ml/)
        2. Modal API service (if MODAL_API_URL is configured)
        3. Mock predictions (development fallback)
        """
        
        # 1. Check for custom local PyTorch model
        if pytorch_model_loader.is_ready():
            try:
                print("[ML] Running inference with custom PyTorch model...")
                return await pytorch_model_loader.predict_batch(image_urls)
            except Exception as e:
                print(f"[WARNING] PyTorch Inference Error: {e}. Falling back...")

        # 2. Real Modal API call
        if self.modal_url and self.modal_url.strip() != "":
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        self.modal_url,
                        json={"image_urls": image_urls}
                    )
                    response.raise_for_status()
                    return response.json()
            except Exception as e:
                print(f"ML Inference Error (Modal): {e}")

        # 3. Fallback to mock predictions
        return self._mock_predictions(image_urls)
    
    def _mock_predictions(self, image_urls: List[str]) -> List[Dict]:
        """
        Generate mock predictions for development/testing
        Returns disease IDs matching the seed data
        """
        disease_options = [
            {"disease_id": 2, "disease_name": "Early Blight", "confidence": 0.87},
            {"disease_id": 3, "disease_name": "Late Blight", "confidence": 0.82},
            {"disease_id": 4, "disease_name": "Bacterial Spot", "confidence": 0.79},
            {"disease_id": 5, "disease_name": "Tomato Mosaic Virus", "confidence": 0.91},
        ]
        
        predictions = []
        for url in image_urls:
            disease = random.choice(disease_options)
            confidence = disease["confidence"] + random.uniform(-0.05, 0.05)
            confidence = max(0.65, min(0.98, confidence))
            
            predictions.append({
                "image_url": url,
                "disease_id": disease["disease_id"],
                "disease_name": disease["disease_name"],
                "confidence_score": round(confidence, 2)
            })
        
        return predictions

ml_service = MLInferenceService()

