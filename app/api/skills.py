from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class SkillAnalysisRequest(BaseModel):
    current_skills: List[str]
    target_role: str
    major: str

class SkillGapResponse(BaseModel):
    missing_skills: List[str]
    action_plan: List[str]
    # recommendations: List[str]

from app.core.recommendation_service import recommendation_service

@router.post("/gap-analysis", response_model=SkillGapResponse)
async def analyze_skill_gap(req: SkillAnalysisRequest):
    result = await recommendation_service.analyze_skill_gap(
        req.current_skills, 
        req.target_role, 
        req.major
    )
    if "error" in result and not result.get("missing_skills"):
        raise HTTPException(status_code=500, detail=result["error"])
    return result

class VerifySkillRequest(BaseModel):
    skill_name: str
    evidence_url: Optional[str] = None
    proof_link: Optional[str] = None # Added alias/field

@router.post("/verify")
async def verify_skill(req: VerifySkillRequest):
    # Mock verification for now
    # In reality, this would save to a 'verification_requests' table
    link = req.evidence_url or req.proof_link
    return {
        "status": "success", 
        "message": f"Skill '{req.skill_name}' marked for verification.",
        "proof_submitted": link
    }
