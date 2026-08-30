from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RecommendationItem(BaseModel):
    id: int = 0
    pesticide_id: Optional[int] = None
    pesticide_name: Optional[str] = None
    type: Optional[str] = None
    active_ingredient: Optional[str] = None
    dosage: Optional[str] = None
    spray_interval: Optional[str] = None
    application_method: Optional[str] = None
    effectiveness: Optional[str] = None
    waiting_period: Optional[str] = None
    precautions: Optional[List[str]] = None
    priority: Optional[int] = None
    crop_stage: Optional[str] = None
    recommendation_note: Optional[str] = None
    fertilizer_id: Optional[int] = None
    fertilizer_name: Optional[str] = None
    composition: Optional[str] = None
    application_stage: Optional[str] = None
    similarity_score: float = 0.95

    class Config:
        from_attributes = True

class PredictionBase(BaseModel):
    image_url: str
    annotated_image_url: Optional[str] = None
    confidence_score: float
    disease_id: Optional[int] = None

class PredictionCreate(PredictionBase):
    user_id: str

class PredictionResponse(BaseModel):
    id: str
    user_id: str
    image_url: str
    annotated_image_url: Optional[str] = None
    disease_id: Optional[int] = None
    disease_name: Optional[str] = None
    confidence_score: float
    created_at: datetime
    recommendations: List[RecommendationItem] = []

    class Config:
        from_attributes = True

class AnalyzeRequest(BaseModel):
    image_urls: List[str]

class AnalyzeResponse(BaseModel):
    predictions: List[PredictionResponse]
    message: str
