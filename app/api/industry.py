from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.db import get_engine
from odmantic import AIOEngine, ObjectId
from app.models.role import Role
from app.models.application import Application, ApplicationStatus
from app.models.user import User, UserRole

router = APIRouter()

@router.get("/dashboard-metrics")
async def get_dashboard_metrics(engine: AIOEngine = Depends(get_engine)):
    total_students = await engine.count(User, User.role == UserRole.STUDENT)
    active_roles = await engine.count(Role, Role.is_active == True)
    
    return {
        "totalStudents": total_students,
        "activeRoles": active_roles,
        "matchesThisWeek": 42,
        "avgMatchScore": 84,
        "topSkills": [
            {"skill": "React", "demand": 95},
            {"skill": "TypeScript", "demand": 88},
            {"skill": "Python", "demand": 85},
            {"skill": "Node.js", "demand": 82},
            {"skill": "AWS", "demand": 78}
        ],
        "recentMatches": [
            {"student": "Alexandra Rivera", "role": "Senior Frontend Engineer", "score": 92, "company": "TechFlow"},
            {"student": "Marcus Chen", "role": "Full Stack Developer", "score": 88, "company": "DataShift"},
            {"student": "Samantha Park", "role": "DevOps Engineer", "score": 91, "company": "CloudTech"}
        ],
        "matchTrend": [
            {"date": "Mon", "matches": 5},
            {"date": "Tue", "matches": 8},
            {"date": "Wed", "matches": 12},
            {"date": "Thu", "matches": 10},
            {"date": "Fri", "matches": 7}
        ],
        "skillDistribution": [
            {"category": "Technical", "count": 156},
            {"category": "Soft Skills", "count": 89},
            {"category": "Design", "count": 45},
            {"category": "Cloud", "count": 67}
        ],
        "hiringPipeline": {
            "applied": 142,
            "message": 45,
            "interviewing": 12,
            "offers": 3
        },
        "recentActivity": [
            {"id": 1, "user": "John Doe", "action": "applied for", "target": "Frontend Engineer", "time": "2 hours ago", "initials": "JD", "color": "blue"},
            {"id": 2, "user": "Alice Smith", "action": "completed", "target": "Technical Assessment", "time": "5 hours ago", "initials": "AS", "color": "green"},
            {"id": 3, "user": "Mike Kim", "action": "accepted interview invite", "target": "", "time": "Yesterday", "initials": "MK", "color": "purple"}
        ]
    }

@router.post("/roles", response_model=Role)
async def create_role(role: Role, engine: AIOEngine = Depends(get_engine)):
    # In a real app, we'd verify the user is INDUSTRY type via auth token
    await engine.save(role)
    return role

@router.get("/roles", response_model=List[Role])
async def get_roles(engine: AIOEngine = Depends(get_engine)):
    return await engine.find(Role)

@router.get("/roles/{role_id}/applications", response_model=List[Application])
async def get_role_applications(role_id: str, engine: AIOEngine = Depends(get_engine)):
    # Verify role belongs to current user
    return await engine.find(Application, Application.role_id == role_id)

@router.put("/applications/{app_id}/status")
async def update_application_status(
    app_id: str, 
    status: ApplicationStatus, 
    engine: AIOEngine = Depends(get_engine)
):
    app = await engine.find_one(Application, Application.id == ObjectId(app_id))
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app.status = status
    await engine.save(app)
    return app
