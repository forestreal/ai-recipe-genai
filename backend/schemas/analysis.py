from pydantic import BaseModel
from typing import List

class CulinaryAnalysis(BaseModel):
    version: str = "v1"
    core_attributes: List[str]
    leaning_cuisines: List[str]
    cooking_styles: List[str]
    ingredient_bias: List[str]
    taste_notes: List[str]
    summary: str