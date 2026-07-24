from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from core.database import get_db
from models.models import User, Token
from auth import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY
)
from schema.user_auth import RefreshTokenRequest, UserCreate, UserLogout, UserSync
from services.user_service import UserService
from utils.db import token_blacklist
from sqlalchemy.orm import Session
from models.user_auth import UserAuth

router = APIRouter(
    prefix="",
    tags=["Authentication"]
)

security = HTTPBearer(auto_error=False)


@router.post("/login", response_model=Token)
async def login(
    user: User,
    db: Session = Depends(get_db)
):

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

    token_expiry = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={"sub": authenticated_user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = create_access_token(
        data={
            "sub": authenticated_user["username"],
            "type": "refresh"
        },
        expires_delta=timedelta(days=7)
    )

    db_user = (
        db.query(UserAuth)
        .filter(UserAuth.id == authenticated_user["id"])
        .first()
    )

    last_login = datetime.utcnow()

    if db_user:
        db_user.access_token = access_token
        db_user.token_type = "bearer"
        db_user.refresh_token = refresh_token
        db_user.token_expiry = token_expiry
        db_user.is_logged_in = True
        db_user.last_login = last_login
        db.commit()

    return {
        "id": authenticated_user["id"],
        "username": authenticated_user["username"],
        "ward": authenticated_user["ward"],
        "zone": authenticated_user["zone"],
        "user_id": authenticated_user["user_id"],
        "surveyor_name": authenticated_user["surveyor_name"],
        "surveyor_id": authenticated_user["surveyor_id"],
        "mobile": authenticated_user["mobile"],
        "email": authenticated_user["email"],
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "token_expiry": token_expiry,
        "is_logged_in": True,
        "last_login": last_login
    }


@router.post("/refresh_token", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            request.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or invalid"
        )

    username = payload.get("sub")
    token_type = payload.get("type")

    if not username or token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    db_user = (
        db.query(UserAuth)
        .filter(UserAuth.username == username)
        .filter(UserAuth.status == "Active")
        .first()
    )

    if not db_user or db_user.refresh_token != request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token does not match active session"
        )

    token_expiry = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={"sub": db_user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    new_refresh_token = create_access_token(
        data={
            "sub": db_user.username,
            "type": "refresh"
        },
        expires_delta=timedelta(days=7)
    )

    db_user.access_token = access_token
    db_user.token_type = "bearer"
    db_user.refresh_token = new_refresh_token
    db_user.token_expiry = token_expiry
    db_user.is_logged_in = True
    db.commit()
    db.refresh(db_user)

    return {
        "id": db_user.id,
        "username": db_user.username,
        "ward": db_user.ward,
        "zone": db_user.zone,
        "user_id": db_user.user_id,
        "surveyor_name": db_user.surveyor_name,
        "surveyor_id": db_user.surveyor_id,
        "mobile": db_user.mobile,
        "email": db_user.email,
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token,
        "token_expiry": token_expiry,
        "is_logged_in": True,
        "last_login": db_user.last_login
    }


@router.post("/logout")
async def logout(
    request: UserLogout | None = None,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db)
):
    username = request.username if request else None

    if not username and credentials:
        try:
            payload = jwt.decode(
                credentials.credentials,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )
            username = payload.get("sub")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired or invalid"
            )

    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or valid token is required"
        )

    if credentials:
        token_blacklist.add(credentials.credentials)

    db_user = (
        db.query(UserAuth)
        .filter(UserAuth.username == username)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db_user.access_token = None
    db_user.token_type = None
    db_user.refresh_token = None
    db_user.token_expiry = None
    db_user.is_logged_in = False
    db.commit()

    return {
        "message": "Successfully logged out"
    }
    
    
@router.post("/register")
def register(
    request: UserCreate,
    db: Session = Depends(get_db)
):
    return UserService(db).create_user(request)


@router.post("/sync_user")
def sync_user(
    request: UserSync,
    db: Session = Depends(get_db)
):
    return UserService(db).sync_sqlite_user(request)
