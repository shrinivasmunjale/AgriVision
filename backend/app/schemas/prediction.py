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

class PredictionCreate(PredictionBase):
    user_id: str

class PredictionResponse(BaseModel):
    id: str
    user_id: str
    image_url: str
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
