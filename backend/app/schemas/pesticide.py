from pydantic import BaseModel, Field
from typing import Optional

class PesticideBase(BaseModel):
    name: str
    active_ingredient: str
    dosage: str
    application_method: str
    suitable_life_stages: list[str] = Field(default_factory=list)

class PesticideCreate(PesticideBase):
    pass

class PesticideUpdate(BaseModel):
    name: Optional[str] = None
    active_ingredient: Optional[str] = None
    dosage: Optional[str] = None
    application_method: Optional[str] = None
    suitable_life_stages: Optional[list[str]] = None

class PesticideResponse(PesticideBase):
    id: int

    class Config:
        from_attributes = True
