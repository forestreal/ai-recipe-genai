from pydantic import BaseModel
from typing import List, Optional

class FlavorAnswer(BaseModel):
    question_id: str
    value: str | int | float | bool | list | None

class FlavorTemplate(BaseModel):
    cuisines: List[str] = []
    heat: Optional[str] = None
    herbs_spices: List[str] = []
    preferred_proteins: List[str] = []
    avoidances: List[str] = []
    allergies: List[str] = []
    dislikes: List[str] = []
    notes: List[str] = []
    locked_at: str

class FlavorLockRequest(BaseModel):
    force: bool = False

class FlavorLockResponse(BaseModel):
    locked: bool
    flavor: FlavorTemplate

