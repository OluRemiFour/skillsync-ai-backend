from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.db import get_engine
from odmantic import AIOEngine, ObjectId
from app.models.role import Role
from app.models.application import Application, ApplicationStatus

router = APIRouter()

@router.post("/roles", response_model=Role)
async def create_role(role: Role, engine: AIOEngine = Depends(get_engine)):
    # In a real app, we'd verify the user is INDUSTRY type via auth token
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
