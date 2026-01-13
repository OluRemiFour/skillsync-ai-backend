from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from app.core.recommendation_service import recommendation_service

router = APIRouter()

class LearningPathRequest(BaseModel):
    skills: List[str]
    goal: str

@router.post("/learning-path")
async def get_learning_path(request: LearningPathRequest):
    result = await recommendation_service.generate_learning_path(request.skills, request.goal)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
