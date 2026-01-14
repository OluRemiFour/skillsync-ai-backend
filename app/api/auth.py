from fastapi import APIRouter, HTTPException, status, Depends, Body, BackgroundTasks
from app.db import get_engine
from odmantic import AIOEngine
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password, create_access_token
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import logging
import random
from datetime import datetime, timedelta
from app.core.email_service import email_service

logger = logging.getLogger(__name__)

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
    is_verified: bool

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

class ProfileStatus(BaseModel):
    is_verified: bool
    is_profile_complete: bool
    missing_fields: List[str]

class SkillUpdate(BaseModel):
    name: str
    level: int
    category: str

class ProfileUpdate(BaseModel):
    bio: Optional[str] = None
    location: Optional[str] = None
    
    # Student fields
    university: Optional[str] = None
    major: Optional[str] = None
    gpa: Optional[float] = None
    graduation_year: Optional[int] = None
    skills: Optional[List[SkillUpdate]] = None
    
    # Industry fields
    company_name: Optional[str] = None
    company_url: Optional[str] = None
    industry_type: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, background_tasks: BackgroundTasks, engine: AIOEngine = Depends(get_engine)):
    logger.info(f"Attempting to register user: {user_data.email}")
    try:
        # Test DB connection
        await engine.client.admin.command('ping')
        
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
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        expiry = datetime.utcnow() + timedelta(minutes=10)
        
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_pw,
            full_name=user_data.name,
            role=user_data.role,
            is_active=True,
            is_verified=False,
            otp=otp,
            otp_expires_at=expiry
        )
        
        logger.info(f"Generated OTP for {user_data.email}: {otp}")
        background_tasks.add_task(email_service.send_otp_email, user_data.email, otp)
        await engine.save(new_user)
    except Exception as e:
        logger.error(f"Registration failure for {user_data.email}: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    
    # Generate token
    access_token = create_access_token(subject=str(new_user.id))
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": str(new_user.id),
        "role": new_user.role,
        "name": new_user.full_name,
        "is_verified": new_user.is_verified
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
        "name": user.full_name,
        "is_verified": user.is_verified
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

@router.post("/send-otp")
async def send_otp(request: ForgotPasswordRequest, background_tasks: BackgroundTasks, engine: AIOEngine = Depends(get_engine)):
    user = await engine.find_one(User, User.email == request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    await engine.save(user)
    
    logger.info(f"Resent OTP for {user.email}: {otp}")
    background_tasks.add_task(email_service.send_otp_email, user.email, otp)
    return {"message": "OTP sent successfully"}

@router.post("/verify-otp")
async def verify_otp(data: OTPVerify, engine: AIOEngine = Depends(get_engine)):
    user = await engine.find_one(User, User.email == data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return {"message": "User already verified"}
        
    if not user.otp or user.otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if not user.otp_expires_at or user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
    
    user.is_verified = True
    user.otp = None
    user.otp_expires_at = None
    await engine.save(user)
    
    return {"message": "Email verified successfully"}

@router.get("/profile-status", response_model=ProfileStatus)
async def get_profile_status(user_id: str, engine: AIOEngine = Depends(get_engine)):
    from odmantic import ObjectId
    user = await engine.find_one(User, User.id == ObjectId(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    missing_fields = []
    if user.role == UserRole.STUDENT:
        if not user.university: missing_fields.append("university")
        if not user.major: missing_fields.append("major")
        if not user.skills: missing_fields.append("skills")
    elif user.role == UserRole.INDUSTRY:
        if not user.company_name: missing_fields.append("company_name")
        if not user.industry_type: missing_fields.append("industry_type")
        
    return {
        "is_verified": user.is_verified,
        "is_profile_complete": len(missing_fields) == 0,
        "missing_fields": missing_fields
    }

@router.put("/update-profile")
async def update_profile(data: ProfileUpdate, user_id: str, engine: AIOEngine = Depends(get_engine)):
    from odmantic import ObjectId
    user = await engine.find_one(User, User.id == ObjectId(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields if provided
    if data.bio is not None: user.bio = data.bio
    if data.location is not None: user.location = data.location
    if data.university is not None: user.university = data.university
    if data.major is not None: user.major = data.major
    if data.gpa is not None: user.gpa = data.gpa
    if data.graduation_year is not None: user.graduation_year = data.graduation_year
    
    if data.skills is not None:
        from app.models.user import Skill
        user.skills = [Skill(name=s.name, level=s.level, category=s.category) for s in data.skills]
        
    if data.company_name is not None: user.company_name = data.company_name
    if data.company_url is not None: user.company_url = data.company_url
    if data.industry_type is not None: user.industry_type = data.industry_type
    
    await engine.save(user)
    return {"message": "Profile updated successfully"}

@router.post("/verify-email")
async def verify_email_token(token: str):
    # Keep this for backward compatibility if needed, but we use OTP now
    return {"message": "Please use OTP verification"}
