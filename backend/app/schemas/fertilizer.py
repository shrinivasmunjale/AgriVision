from pydantic import BaseModel
from typing import Optional

class FertilizerBase(BaseModel):
    name: str
    active_ingredient: str
    dosage: str
    application_method: str
    suitable_life_stages: list[str] = []

class FertilizerCreate(FertilizerBase):
    pass

class FertilizerUpdate(BaseModel):
    name: Optional[str] = None
    active_ingredient: Optional[str] = None
    dosage: Optional[str] = None
    application_method: Optional[str] = None
    suitable_life_stages: Optional[list[str]] = None

class FertilizerResponse(FertilizerBase):
    id: int

    class Config:
        from_attributes = True
