import asyncio
from app.db import engine
from app.models.user import User, UserRole, Skill
from app.models.role import Role, RoleType
from app.core.security import get_password_hash

async def seed_data():
    print("Seeding data...")
    
    # Check if data exists
    existing_users = await engine.find(User)
    if existing_users:
        print("Data already exists. Skipping seed.")
        return

    # Create Students
    students_data = [
        {
            "email": "alexandra.rivera@university.edu", "full_name": "Alexandra Rivera", "university": "Stanford University",
            "skills": [
                {"name": "React", "level": 92, "verified": True},
                {"name": "TypeScript", "level": 88, "verified": True},
                {"name": "Node.js", "level": 85, "verified": True}
            ]
        },
        {
            "email": "marcus.chen@tech.edu", "full_name": "Marcus Chen", "university": "MIT",
            "skills": [
                {"name": "Python", "level": 94, "verified": True},
                {"name": "Django", "level": 90, "verified": True},
                {"name": "PostgreSQL", "level": 85, "verified": True}
            ]
        },
        {
            "email": "samantha.park@university.edu", "full_name": "Samantha Park", "university": "UC Berkeley",
            "skills": [
                {"name": "AWS", "level": 95, "verified": True},
                {"name": "Kubernetes", "level": 90, "verified": True},
                {"name": "Docker", "level": 92, "verified": True}
            ]
        }
    ]

    for s in students_data:
        user = User(
            email=s["email"],
            hashed_password=get_password_hash("password123"),
            full_name=s["full_name"],
            role=UserRole.STUDENT,
            university=s["university"],
            skills=[Skill(**skill) for skill in s["skills"]]
        )
        await engine.save(user)
        print(f"Created student: {s['full_name']}")

    # Create Industry
    industry_user = User(
        email="recruiter@techflow.com",
        hashed_password=get_password_hash("password123"),
        full_name="TechFlow Recruiter",
        role=UserRole.INDUSTRY,
        company_name="TechFlow Systems"
    )
    await engine.save(industry_user)
    print(f"Created recruiter: {industry_user.full_name}")

    # Create Roles
    roles_data = [
        {
            "title": "Senior Frontend Engineer",
            "company_name": "TechFlow Systems",
            "description": "Lead frontend development...",
            "required_skills": ["React", "TypeScript", "CSS", "REST APIs"],
            "role_type": RoleType.FULL_TIME,
            "location": "Remote",
            "min_experience_years": 5
        },
        {
            "title": "Backend Developer",
            "company_name": "TechFlow Systems",
            "description": "Build scalable APIs...",
            "required_skills": ["Python", "Django", "SQL"],
            "role_type": RoleType.FULL_TIME,
            "location": "Hybrid",
            "min_experience_years": 3
        }
    ]

    for r in roles_data:
        role = Role(
            title=r["title"],
            company_name=r["company_name"],
            recruiter_id=str(industry_user.id),
            description=r["description"],
            required_skills=r["required_skills"],
            role_type=r["role_type"],
            location=r["location"],
            min_experience_years=r["min_experience_years"]
        )
        await engine.save(role)
        print(f"Created role: {r['title']}")

    print("Seeding complete.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(seed_data())
