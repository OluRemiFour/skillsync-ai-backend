from typing import Optional, List
from sqlmodel import SQLModel, Field
from datetime import datetime

class ScholarshipBase(SQLModel):
    title: str
    provider: str
    amount: Optional[str] = None
    deadline: Optional[str] = None
    url: str
    description: Optional[str] = None
    match_score: Optional[int] = 0
    tags: str = "" 

class Scholarship(ScholarshipBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class ScholarshipCreate(ScholarshipBase):
    pass
