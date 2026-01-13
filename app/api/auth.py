from fastapi import APIRouter, HTTPException, status, Depends, Body
from app.db import get_engine
from odmantic import AIOEngine
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password, create_access_token
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    name: str
    role: UserRole

    # Simple validator to ensure passwords match
    def check_passwords(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    role: str
    name: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, engine: AIOEngine = Depends(get_engine)):
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check existing
    existing_user = await engine.find_one(User, User.email == user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_pw = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        full_name=user_data.name,
        role=user_data.role,
        is_active=True # Auto-active for now, verification can be a step
    )
    
    await engine.save(new_user)
    
    # Generate token
    access_token = create_access_token(subject=str(new_user.id))
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": str(new_user.id),
        "role": new_user.role,
        "name": new_user.full_name
    }

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, engine: AIOEngine = Depends(get_engine)):
    user = await engine.find_one(User, User.email == login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(subject=str(user.id))
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user_id": str(user.id),
        "role": user.role,
        "name": user.full_name
    }

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, engine: AIOEngine = Depends(get_engine)):
    user = await engine.find_one(User, User.email == request.email)
    if not user:
        # Don't reveal if user exists
        return {"message": "If this email is registered, you will receive password reset instructions."}
    
    # TODO: Implement actual email sending
    # For now, we simulate success
    return {"message": "If this email is registered, you will receive password reset instructions."}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, engine: AIOEngine = Depends(get_engine)):
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
        
    # TODO: Verify token and update password
    # This is a stub implementation
    return {"message": "Password has been reset successfully"}

@router.post("/verify-email")
async def verify_email(token: str):
    # TODO: Verify email token
    return {"message": "Email verified successfully"}
