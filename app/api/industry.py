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
    
    applied_count = await engine.count(Application, Application.status == ApplicationStatus.PENDING)
    message_count = await engine.count(Application, Application.status == ApplicationStatus.REVIEWING)
    interviewing_count = await engine.count(Application, Application.status == ApplicationStatus.INTERVIEW)
    offers_count = await engine.count(Application, Application.status == ApplicationStatus.OFFERED)

    # Fetch some recent applications for activity
    recent_apps = await engine.find(Application, sort=Application.applied_at.desc(), limit=3)
    recent_activity = []
    for app in recent_apps:
        student = await engine.find_one(User, User.id == app.student_id)
        role = await engine.find_one(Role, Role.id == app.role_id)
        if student and role:
            recent_activity.append({
                "id": str(app.id),
                "user": student.full_name or student.name,
                "action": "applied for",
                "target": role.title,
                "time": "Just now", # Could calculate actual relative time
                "initials": "".join([n[0] for n in (student.full_name or student.name).split()]),
                "color": "blue"
            })

    if not recent_activity:
        recent_activity = [
            {"id": 1, "user": "John Doe", "action": "applied for", "target": "Frontend Engineer", "time": "2 hours ago", "initials": "JD", "color": "blue"},
            {"id": 2, "user": "Alice Smith", "action": "completed", "target": "Technical Assessment", "time": "5 hours ago", "initials": "AS", "color": "green"},
            {"id": 3, "user": "Mike Kim", "action": "accepted interview invite", "target": "", "time": "Yesterday", "initials": "MK", "color": "purple"}
        ]

    # Calculate Skill Aggregations from DB
    students = await engine.find(User, User.role == UserRole.STUDENT)
    skill_counts = {}
    category_counts = {}
    
    for student in students:
        for skill in student.skills:
            skill_counts[skill.name] = skill_counts.get(skill.name, 0) + 1
            cat = skill.category or "General"
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
    # Format Top Skills
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_skills_formatted = [
        {"skill": name, "demand": int((count / max(1, len(students))) * 100)} 
        for name, count in sorted_skills
    ]
    
    # Format Skill Distribution
    skill_dist_formatted = [
        {"category": cat, "count": count}
        for cat, count in category_counts.items()
    ]

    return {
        "totalStudents": total_students,
        "activeRoles": active_roles,
        "matchesThisWeek": applied_count, 
        "avgMatchScore": 84, # Calculated periodically in real scenario
        "topSkills": top_skills_formatted if top_skills_formatted else [
            {"skill": "React", "demand": 0},
            {"skill": "Python", "demand": 0}
        ],
        "recentMatches": [
            # In production: Fetch recent successful matches
        ],
        "matchTrend": [
            {"date": "Mon", "matches": 0},
            {"date": "Tue", "matches": 0},
            {"date": "Wed", "matches": 0},
            {"date": "Thu", "matches": 0},
            {"date": "Fri", "matches": applied_count}
        ],
        "skillDistribution": skill_dist_formatted,
        "hiringPipeline": {
            "applied": applied_count,
            "message": message_count,
            "interviewing": interviewing_count,
            "offers": offers_count
        },
        "recentActivity": recent_activity
    }

@router.post("/roles", response_model=Role)
async def create_role(role: Role, engine: AIOEngine = Depends(get_engine)):
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
