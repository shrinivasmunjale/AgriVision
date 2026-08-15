from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RecommendationItem(BaseModel):
    id: int
    pesticide_id: Optional[int] = None
    pesticide_name: Optional[str] = None
    fertilizer_id: Optional[int] = None
    fertilizer_name: Optional[str] = None
    similarity_score: float

    class Config:
        from_attributes = True

class PredictionBase(BaseModel):
    image_url: str
    confidence_score: float
    disease_id: Optional[int] = None
    crop_age_days: Optional[int] = None
    life_stage: Optional[str] = None

class PredictionCreate(PredictionBase):
    user_id: str

class PredictionResponse(BaseModel):
    id: str
    user_id: str
    image_url: str
    disease_id: Optional[int] = None
    disease_name: Optional[str] = None
    confidence_score: float
    crop_age_days: Optional[int] = None
    life_stage: Optional[str] = None
    created_at: datetime
    recommendations: List[RecommendationItem] = []
    disease_details: Optional[dict] = None

    class Config:
        from_attributes = True

class AnalyzeRequest(BaseModel):
    image_urls: List[str]
    crop_age_days: Optional[int] = None
    life_stage: Optional[str] = None

class AnalyzeResponse(BaseModel):
    success: bool = True
    predictions: List[PredictionResponse] = []
    message: str
    warning: Optional[str] = None
