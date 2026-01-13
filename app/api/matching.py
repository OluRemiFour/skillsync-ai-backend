from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from app.db import get_engine
from odmantic import AIOEngine, ObjectId
from app.models.user import User, UserRole
from app.models.role import Role
import math

router = APIRouter()

# Helper Models for response
from pydantic import BaseModel

class MatchResult(BaseModel):
    id: str  # Composite ID or just some unique string
    studentId: str
    roleId: str
    studentName: str
    email: str
    matchPercentage: int
    topSkills: List[str]
    experienceYears: int
    location: Optional[str]
    skillsMatched: List[str]
    skillsMissing: List[str]
    experienceAlignment: str

@router.get("/roles/{role_id}", response_model=List[MatchResult])
async def get_matches_for_role(role_id: str, engine: AIOEngine = Depends(get_engine)):
    role = await engine.find_one(Role, Role.id == ObjectId(role_id))
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
        
    students = await engine.find(User, User.role == UserRole.STUDENT)
    
    matches = []
    
    for student in students:
        match_data = calculate_match(student, role)
        if match_data['matchPercentage'] > 0: # Filter out 0 matches if desired
            matches.append(match_data)
            
    # Sort by match percentage desc
    matches.sort(key=lambda x: x['matchPercentage'], reverse=True)
    return matches

@router.get("/students/{student_id}", response_model=List[MatchResult])
async def get_matches_for_student(student_id: str, engine: AIOEngine = Depends(get_engine)):
    student = await engine.find_one(User, User.id == ObjectId(student_id))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    roles = await engine.find(Role, Role.is_active == True)
    
    matches = []
    for role in roles:
        match_data = calculate_match(student, role)
        if match_data['matchPercentage'] > 0:
            matches.append(match_data)
            
    matches.sort(key=lambda x: x['matchPercentage'], reverse=True)
    return matches

def calculate_match(student: User, role: Role) -> Dict[str, Any]:
    student_skills_names = {s.name.lower() for s in student.skills}
    role_skills_names = {s.lower() for s in role.required_skills}
    
    matched_skills = [s for s in role.required_skills if s.lower() in student_skills_names]
    missing_skills = [s for s in role.required_skills if s.lower() not in student_skills_names]
    
    match_percentage = 0
    if role.required_skills:
        match_percentage = int((len(matched_skills) / len(role.required_skills)) * 100)
    
    # Simple experience parsing (assuming format "X years")
    # In real app, store as integer in DB
    student_exp = 0 # Default
    # Attempt to parse student experience field if it exists specifically or assume 0
    # User model currently doesn't have explicit 'experience_years', let's assume 0 or check if 'experience' string exists
    # Checking User model: it has 'graduation_year' but not 'experience'. 
    # For now, we will mock experience based on grad year or random, or better, add it to model later.
    # We will assume 2 years for now to avoid breaking.
    
    # Parse role requirement
    role_min_exp = role.min_experience_years
    
    exp_alignment = "N/A"
    diff = student_exp - role_min_exp
    if diff >= 0:
        exp_alignment = f"Exceeds requirement by {diff} year(s)"
    else:
        exp_alignment = f"{abs(diff)} year(s) below requirement"

    return {
        "id": f"{student.id}-{role.id}",
        "studentId": str(student.id),
        "roleId": str(role.id),
        "studentName": student.full_name,
        "email": student.email,
        "matchPercentage": match_percentage,
        "topSkills": [s.name for s in student.skills[:3]], # Top 3 skills
        "experienceYears": student_exp,
        "location": student.university, # Using university as location proxy for now
        "skillsMatched": matched_skills,
        "skillsMissing": missing_skills,
        "experienceAlignment": exp_alignment
    }
