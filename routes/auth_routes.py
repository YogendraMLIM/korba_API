from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.database import get_db
from models.models import User, Token
from auth import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from schema.user_auth import UserCreate
from services.user_service import UserService
from utils.db import token_blacklist
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="",
    tags=["Authentication"]
)

security = HTTPBearer()


@router.post("/login", response_model=Token)
async def login(user: User):

    authenticated_user = authenticate_user(
        user.username,
        user.password
    )

    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": authenticated_user["username"]},
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    return {
        "username": authenticated_user["username"],
        "ward": authenticated_user["ward"],
        "zone": authenticated_user["zone"],
        "surveyor_name": authenticated_user["surveyor_name"],
        "surveyor_id": authenticated_user["surveyor_id"],
        "mobile": authenticated_user["mobile"],
        "email": authenticated_user["email"],
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token_blacklist.add(credentials.credentials)

    return {
        "message": "Successfully logged out"
    }
    
    
@router.post("/register")
def register(
    request: UserCreate,
    db: Session = Depends(get_db)
):
    return UserService(db).create_user(request)