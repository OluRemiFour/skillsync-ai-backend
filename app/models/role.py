from typing import List, Optional
from odmantic import Model, Field
from datetime import datetime
from enum import Enum

class RoleType(str, Enum):
    INTERNSHIP = "internship"
    FULL_TIME = "full_time"
    PART_TIME = "part_time"

class Role(Model):
    title: str
    company_name: str
    recruiter_id: str 
    description: str
    requirements: List[str] = []
    role_type: RoleType
    location: str
    salary_range: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Matching criteria
    required_skills: List[str] = []
    min_experience_years: int = 0
