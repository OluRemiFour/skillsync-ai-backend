from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SkillSync API",
    description="Backend API for SkillSync with Talent Matching and Scraper capabilities",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:5173", 
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api import scholarships, industry, recommendation, internships, communication, auth, students, matching

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(matching.router, prefix="/api/matches", tags=["matches"])
app.include_router(scholarships.router, prefix="/api/scholarships", tags=["scholarships"])
app.include_router(internships.router, prefix="/api/internships", tags=["internships"])
app.include_router(industry.router, prefix="/api/industry", tags=["industry"])
app.include_router(recommendation.router, prefix="/api/recommendation", tags=["recommendation"])
app.include_router(communication.router, prefix="/api/communication", tags=["communication"])

@app.get("/")
async def root():
    return {"message": "SkillSync API is running", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
