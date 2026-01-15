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
    recommendations: List[str]

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
