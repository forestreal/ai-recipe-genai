from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

Somato = Literal["ectomorph","mesomorph","endomorph","mixed"]
Goal   = Literal["fat_loss","muscle_gain","recomp","performance","maintenance"]

class EvaluationRequest(BaseModel): force: bool = False

class CoreStats(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bone_structure: Optional[str] = None
    fat_distribution: Optional[str] = None
    muscle_gain: Optional[str] = None
    carb_response: Optional[str] = None
    post_meal_energy: Optional[str] = None
    flexibility: Optional[str] = None
    training_time: Optional[str] = None

class Personality(BaseModel):
    vibe_line: Optional[str] = None
    style: Literal["concise","snark","gentle","matter"] = "concise"

class EvaluationSnapshot(BaseModel):
    somatotype: Somato
    fitness_goal: Goal
    core: CoreStats
    persona: Personality
    constraints: Dict[str, Any] = Field(default_factory=dict)
    notes: List[str] = Field(default_factory=list)
    version: str = "v1"
    locked_at: Optional[str] = None

class EvaluationResponse(BaseModel):
    locked: bool
    evaluation: EvaluationSnapshot
    public_summary: Dict[str, Any]