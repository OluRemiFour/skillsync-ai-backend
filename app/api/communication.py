from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from app.db import get_engine
from odmantic import AIOEngine
from app.models.application import Application, ApplicationStatus

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
    # In production: Integrate with SendGrid/Twilio/SMTP
    print(f"Sending message to {req.student_email}: {req.message}")
    return {"status": "success", "message": f"Message sent to {req.student_name}"}

@router.post("/interview")
async def schedule_interview(req: InterviewRequest):
    """
    Simulates scheduling an interview.
    """
    # In production: Create calendar invite, send email, save to DB
    print(f"Scheduling interview with {req.student_email} on {req.date} at {req.time}")
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
