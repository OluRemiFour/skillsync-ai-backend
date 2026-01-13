from odmantic import Model, Field
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    INTERVIEW = "interview"
    OFFERED = "offered"
    REJECTED = "rejected"

class Application(Model):
    student_id: str
    role_id: str
    status: ApplicationStatus = ApplicationStatus.PENDING
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    match_score: int 
    cover_letter: str = ""
