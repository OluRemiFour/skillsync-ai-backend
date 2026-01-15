from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from app.db import get_engine
from odmantic import AIOEngine
from app.models.application import Application, ApplicationStatus
from app.core.email_service import email_service
from typing import List

router = APIRouter()

# Data Models
class MessageRequest(BaseModel):
    student_id: str
    student_email: str
    student_name: str
    message: str
    sender_id: str # Recruiter ID
    
class ApplyRequest(BaseModel):
    role_id: str
    student_id: str
    message: str = ""

class InterviewRequest(BaseModel):
    student_id: str
    student_email: str
    date: str
    time: str
    type: str # 'Video', 'Phone'
    notes: str = ""

@router.post("/message")
async def send_message(req: MessageRequest):
    """
    Simulates sending an email/message to a student.
    """
    success = await email_service.send_general_email(
        to_email=req.student_email,
        subject="Message from SkillSync Recruiter",
        student_name=req.student_name,
        content=req.message
    )
    if not success:
        return {"status": "error", "message": "Failed to send email"}
    return {"status": "success", "message": f"Message sent to {req.student_name}"}

@router.post("/interview")
async def schedule_interview(req: InterviewRequest):
    """
    Simulates scheduling an interview.
    """
    success = await email_service.send_interview_email(
        to_email=req.student_email,
        student_name="Student", # We might want to pass name in request
        date=req.date,
        time=req.time,
        invite_type=req.type,
        notes=req.notes
    )
    if not success:
        return {"status": "error", "message": "Failed to send interview invitation"}
        
    return {
        "status": "success", 
        "message": f"Interview scheduled for {req.date} at {req.time}. Invite sent to {req.student_email}."
    }

@router.post("/apply")
async def apply_for_role(req: ApplyRequest, engine: AIOEngine = Depends(get_engine)):
    """
    Saves a job application to the database.
    """
    application = Application(
        student_id=req.student_id,
        role_id=req.role_id,
        cover_letter=req.message,
        match_score=85, # Default/Calculated score
        status=ApplicationStatus.PENDING
    )
    await engine.save(application)
    return {"status": "success", "message": "Application submitted successfully"}

@router.get("/applications/student/{student_id}", response_model=List[Application])
async def get_student_applications(student_id: str, engine: AIOEngine = Depends(get_engine)):
    """
    Fetches all applications for a specific student.
    """
    applications = await engine.find(Application, Application.student_id == student_id)
    return applications
