from pydantic import BaseModel
from typing import Optional, List

class DiseaseBase(BaseModel):
    name: str
    description: str
    symptoms: str
    causes: str
    severity_level: str
    reference_image_url: Optional[str] = None

class DiseaseCreate(DiseaseBase):
    pass

class DiseaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    symptoms: Optional[str] = None
    causes: Optional[str] = None
    severity_level: Optional[str] = None
    reference_image_url: Optional[str] = None

class DiseaseResponse(DiseaseBase):
    id: int

    class Config:
        from_attributes = True
