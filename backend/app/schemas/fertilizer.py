from pydantic import BaseModel
from typing import Optional

class FertilizerBase(BaseModel):
    name: str
    composition: str
    dosage: str
    application_stage: str

class FertilizerCreate(FertilizerBase):
    pass

class FertilizerUpdate(BaseModel):
    name: Optional[str] = None
    composition: Optional[str] = None
    dosage: Optional[str] = None
    application_stage: Optional[str] = None

class FertilizerResponse(FertilizerBase):
    id: int

    class Config:
        from_attributes = True
