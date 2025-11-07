from pydantic import BaseModel
from typing import List

class Ingredient(BaseModel):
    item: str
    quantity: float | int | str
    unit: str | None = None

class Macros(BaseModel):
    calories: int | float
    protein_g: int | float
    carbs_g: int | float
    fat_g: int | float
    fiber_g: int | float

class RecipeOut(BaseModel):
    title: str
    cuisine: str
    meal_type: str
    prep_time: str
    difficulty: str
    ingredients: List[Ingredient]
    instructions: List[str]
    macros: Macros
    micros_highlights: List[str]
    timing: str
    notes: str