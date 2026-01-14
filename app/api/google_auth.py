from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.config import settings
from app.models.user import User, UserRole
from app.api.auth import create_access_token
from odmantic import AIOEngine
from app.db import get_engine
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

from typing import Optional

class GoogleAuthRequest(BaseModel):
    id_token: str
    role: Optional[str] = None # 'student' or 'industry'

@router.post("/google")
async def google_auth(
    auth_data: GoogleAuthRequest,
    engine: AIOEngine = Depends(get_engine)
):
    try:
        # Verify the ID token from Google
        idinfo = id_token.verify_oauth2_token(
            auth_data.id_token, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid; extract user info
        email = idinfo['email']
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')

        # Check if user exists
        user = await engine.find_one(User, User.email == email)

        if not user:
            # If user doesn't exist, we MUST have a role to create them
            if not auth_data.role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ROLE_REQUIRED"
                )
            
            # Create new user
            user = User(
                email=email,
                name=name,
                role=auth_data.role,
                is_verified=True, # Google users are pre-verified
                avatar=picture,
                hashed_password="" # No password for Google users
            )
            await engine.save(user)
            logger.info(f"Created new Google user: {email}")
        else:
            # Update role only if provided and different? 
            # Or just ignore role if they already exist
            if auth_data.role and user.role != auth_data.role:
                user.role = auth_data.role
            
            user.avatar = picture
            await engine.save(user)
            logger.info(f"Google login for existing user: {email}")

        # Create access token
        access_token = create_access_token(data={"sub": user.email})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "name": user.name,
            "role": user.role,
            "is_verified": user.is_verified
        }

    except ValueError as e:
        logger.error(f"Google token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )
    except Exception as e:
        logger.error(f"Google auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during Google auth",
        )
