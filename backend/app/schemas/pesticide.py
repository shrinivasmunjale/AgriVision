from pydantic import BaseModel
from typing import Optional

class PesticideBase(BaseModel):
    name: str
    active_ingredient: str
    dosage: str
    application_method: str

class PesticideCreate(PesticideBase):
    pass

class PesticideUpdate(BaseModel):
    name: Optional[str] = None
    active_ingredient: Optional[str] = None
    dosage: Optional[str] = None
    application_method: Optional[str] = None

class PesticideResponse(PesticideBase):
    id: int

    class Config:
        from_attributes = True
