from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

class Question(BaseModel):
    id: str
    type: Literal["text","number","choice","llm_trigger"]
    question: str
    options: Optional[List[str]] = None

class YapRequest(BaseModel):
    question: Question
    user_message: str = Field(..., max_length=1000)
    context: Dict[str, Any] = {}

class YapPublicResponse(BaseModel):
    display_reply: str = Field(..., max_length=650)
    tone: Literal["polymath","snark","gentle","neutral","disregard"] = "neutral"
    relation: Literal["related","offtopic","none"] = "none"
    commit: Dict[str, Any] = {"applied": False, "ids": []}