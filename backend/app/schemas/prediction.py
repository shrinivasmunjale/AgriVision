from pydantic import BaseModel
from typing import Optional, List, Dict, Union
from datetime import datetime

class RecommendationItem(BaseModel):
    id: int
    pesticide_id: Optional[int] = None
    pesticide_name: Optional[str] = None
    fertilizer_id: Optional[int] = None
    fertilizer_name: Optional[str] = None
    active_ingredient: Optional[str] = None
    dosage: Optional[str] = None
    application_method: Optional[str] = None
    suitable_life_stages: Optional[Union[str, List[str]]] = None
    similarity_score: float

    class Config:
        from_attributes = True

class BoundingBox(BaseModel):
    box_2d: List[float]  # [ymin, xmin, ymax, xmax] normalized (0.0 to 1.0)
    label: str
    confidence: float
    disease_id: Optional[int] = None
    box_pixels: Optional[List[float]] = None
    class_id: Optional[int] = None

class PredictionBase(BaseModel):
    image_url: str
    confidence_score: float
    disease_id: Optional[int] = None
    crop_age_days: Optional[int] = None
    life_stage: Optional[str] = None
    bounding_boxes: Optional[List[Dict]] = []

class PredictionCreate(PredictionBase):
    user_id: str

class PredictionResponse(BaseModel):
    id: str
    user_id: str
    image_url: str
    disease_id: Optional[int] = None
    disease_name: Optional[str] = None
    confidence_score: float
    bounding_boxes: Optional[List[Dict]] = []
    crop_age_days: Optional[int] = None
    life_stage: Optional[str] = None
    created_at: datetime
    recommendations: List[RecommendationItem] = []
    disease_details: Optional[dict] = None

    class Config:
        from_attributes = True

class AnalyzeRequest(BaseModel):
    image_urls: List[str]
    filenames: Optional[List[str]] = None
    crop_age_days: Optional[int] = None
    life_stage: Optional[str] = None

class IgnoredItem(BaseModel):
    filename: str
    reason: str

class AnalyzeResponse(BaseModel):
    success: bool = True
    valid_predictions: List[PredictionResponse] = []
    predictions: List[PredictionResponse] = []
    ignored_images: List[IgnoredItem] = []
    disease_summary: Dict[str, List[str]] = {}
    total_uploaded: int = 0
    processed: int = 0
    ignored: int = 0
    healthy: int = 0
    infected: int = 0
    message: str
    warning: Optional[str] = None

class BatchReportRequest(BaseModel):
    total_uploaded: int = 0
    processed: int = 0
    ignored: int = 0
    healthy: int = 0
    infected: int = 0
    disease_summary: Dict[str, List[str]] = {}
    ignored_images: List[IgnoredItem] = []
    valid_predictions: Optional[List[Dict]] = []
    predictions: Optional[List[Dict]] = []
