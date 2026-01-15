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

@router.post("/analyze", response_model=SkillGapResponse)
async def analyze_skill_gap(request: SkillAnalysisRequest):
    """
    Uses Gemini AI to analyze skill gaps based on current skills and target role.
    """
    from app.core.config import settings
    
    # Default fallback
    response = SkillGapResponse(
        missing_skills=["Advanced Project Management", "System Design"],
        action_plan=["Take a course on System Design", "Build a complex project"],
        recommendations=["Coursera: System Design", "EdX: Agile Management"]
    )

    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            prompt = (
                f"Act as a career coach. Analyze a student majoring in {request.major} "
                f"who wants to be a {request.target_role}. "
                f"They currently have these skills: {', '.join(request.current_skills)}. "
                f"Identify 3-5 critical missing skills, a 3-step action plan, and 2 specific course recommendations. "
                f"Return a strict JSON object with keys: 'missing_skills' (list of strings), "
                f"'action_plan' (list of strings), 'recommendations' (list of strings). "
                f"Do not use markdown formatting."
            )
            
            ai_resp = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            if ai_resp.text:
                import json
                cleaned = ai_resp.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(cleaned)
                response = SkillGapResponse(**data)
                
        except Exception as e:
            print(f"AI Analysis failed: {e}")
            
    return response

@router.post("/verify")
async def verify_skill(req: VerifySkillRequest):
    # Mock verification for now
    return {"status": "success", "message": f"Skill '{req.skill_name}' marked for verification."}
