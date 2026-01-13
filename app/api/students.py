from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.db import get_engine
from odmantic import AIOEngine, ObjectId
from app.models.user import User, UserRole

router = APIRouter()

@router.get("/", response_model=List[User])
async def get_students(engine: AIOEngine = Depends(get_engine)):
    # Fetch only students
    students = await engine.find(User, User.role == UserRole.STUDENT)
    return students

@router.get("/{id}", response_model=User)
async def get_student(id: str, engine: AIOEngine = Depends(get_engine)):
    student = await engine.find_one(User, User.id == ObjectId(id), User.role == UserRole.STUDENT)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.get("/search", response_model=List[User])
async def search_students(query: str, engine: AIOEngine = Depends(get_engine)):
    # Simple regex search on name or email
    # Note: Regex queries can be slow on large datasets without text indexes
    students = await engine.find(
        User, 
        (User.role == UserRole.STUDENT) & 
        (
            { "full_name": { "$regex": query, "$options": "i" } } 
            | { "email": { "$regex": query, "$options": "i" } }
        )
    )
    return students
