from typing import Optional, List
from odmantic import Model, Field
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    INDUSTRY = "industry"
    ADMIN = "admin"

class Skill(Model):
    name: str
    level: int  # 1-100
    verified: bool = False

class User(Model):
    email: str = Field(unique=True)
    hashed_password: str
    full_name: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Student Profile Fields
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    skills: List[Skill] = []
    
    # Industry Profile Fields
    company_name: Optional[str] = None
    company_url: Optional[str] = None
    industry_type: Optional[str] = None
