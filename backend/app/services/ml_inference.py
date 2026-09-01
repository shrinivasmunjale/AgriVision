import httpx
from app.core.config import settings
from app.ml.model_loader import pytorch_model_loader
from typing import List, Dict, Optional
import random

class MLInferenceService:
    def __init__(self):
        self.modal_url = settings.MODAL_API_URL
        self.confidence_threshold = 0.50
    
    async def predict_disease(self, image_urls: List[str], filenames: Optional[List[str]] = None) -> Dict:
        """
        Predict disease from images. Order of priority:
        1. Local custom PyTorch model (YOLOv8 leaf check -> EfficientNetB0 disease classification)
        2. Modal API service (if MODAL_API_URL is configured)
        3. Mock predictions (development fallback)

        Returns an aggregated structure:
            {"valid_predictions": [...], "ignored_images": [...]}
        """

        # 1. Check for custom local PyTorch model
        if pytorch_model_loader.is_ready():
            try:
                print("[ML] Running two-stage inference (YOLOv8 -> EfficientNetB0)...")
                return await pytorch_model_loader.predict_batch(image_urls, filenames)
            except Exception as e:
                print(f"[WARNING] PyTorch Inference Error: {e}. Falling back...")

        # 2. Real Modal API call
        if self.modal_url and self.modal_url.strip() != "":
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        self.modal_url,
                        json={"image_urls": image_urls, "filenames": filenames}
                    )
                    response.raise_for_status()
                    return self._normalize_batch(response.json(), image_urls, filenames)
            except Exception as e:
                print(f"ML Inference Error (Modal): {e}")

        # 3. Fallback to mock predictions
        return self._mock_predictions(image_urls, filenames)

    def _normalize_batch(self, data, image_urls: List[str], filenames: Optional[List[str]] = None) -> Dict:
        """Normalize raw inference output into {valid_predictions, ignored_images}."""
        if isinstance(data, dict) and (
            "valid_predictions" in data or "ignored_images" in data
        ):
            return {
                "valid_predictions": data.get("valid_predictions", []),
                "ignored_images": data.get("ignored_images", []),
            }

        # Assume a flat list of {success/message/disease_id/...}
        if isinstance(data, list):
            valid = []
            ignored = []
            for idx, item in enumerate(data):
                fname = filenames[idx] if filenames and idx < len(filenames) else None
                if item.get("status") == "valid" or item.get("success") is True:
                    valid.append({
                        "status": "valid",
                        "image_url": item.get("image_url", image_urls[idx] if idx < len(image_urls) else ""),
                        "filename": item.get("filename") or self._derive_name(image_urls[idx] if idx < len(image_urls) else "", fname),
                        "disease_id": item.get("disease_id"),
                        "disease_name": item.get("disease_name"),
                        "confidence_score": item.get("confidence_score", 0.0),
                        "bounding_boxes": item.get("bounding_boxes", []),
                    })
                else:
                    ignored.append({
                        "status": "ignored",
                        "image_url": item.get("image_url", image_urls[idx] if idx < len(image_urls) else ""),
                        "filename": item.get("filename") or self._derive_name(image_urls[idx] if idx < len(image_urls) else "", fname),
                        "reason": item.get("reason") or item.get("message") or "Invalid image",
                        "confidence_score": item.get("confidence_score", 0.0),
                        "bounding_boxes": item.get("bounding_boxes", []),
                    })
            return {"valid_predictions": valid, "ignored_images": ignored}

        return {"valid_predictions": [], "ignored_images": []}

    @staticmethod
    def _derive_name(image_url: str, filename: Optional[str] = None) -> str:
        if filename and str(filename).strip():
            return str(filename)
        from urllib.parse import urlparse
        base = urlparse(image_url).path
        return base.split("/")[-1] or "image"

    def _mock_predictions(self, image_urls: List[str], filenames: Optional[List[str]] = None) -> Dict:
        """
        Generate mock predictions for development/testing
        """
        disease_options = [
            {"disease_id": 2, "disease_name": "Early Blight", "confidence": 0.87},
            {"disease_id": 3, "disease_name": "Late Blight", "confidence": 0.82},
            {"disease_id": 4, "disease_name": "Bacterial Spot", "confidence": 0.79},
            {"disease_id": 5, "disease_name": "Tomato Mosaic Virus", "confidence": 0.91},
        ]

        valid_predictions = []
        for idx, url in enumerate(image_urls):
            disease = random.choice(disease_options)
            confidence = round(disease["confidence"] + random.uniform(-0.05, 0.05), 2)
            fname = filenames[idx] if filenames and idx < len(filenames) else None

            valid_predictions.append({
                "status": "valid",
                "image_url": url,
                "filename": self._derive_name(url, fname),
                "disease_id": disease["disease_id"],
                "disease_name": disease["disease_name"],
                "confidence_score": round(max(0.70, confidence), 4),
                "bounding_boxes": []
            })

        return {"valid_predictions": valid_predictions, "ignored_images": []}

ml_service = MLInferenceService()
