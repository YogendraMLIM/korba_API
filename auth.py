import os
from datetime import datetime, timedelta
from typing import Optional
from utils.db import get_engine
from jose import jwt, JWTError
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def get_user(username: str, password: str):

    engine = get_engine()

    query = text("""
        SELECT 
            zone,
            ward,
            surveyor_name,
            surveyor_id,
            username,
            mobile,
            email
        FROM propertytax.user_auth
        WHERE username = :username
          AND password = :password
          AND status = 'Active'
    """)

    with engine.connect() as conn:

        result = conn.execute(
            query,
            {
                "username": username,
                "password": password
            }
        )

        row = result.fetchone()


    if row is None:
        return None

    print("User authenticated successfully:", row)
    return {
        "username": row.username,
        "ward": row.ward,
        "zone": row.zone,
        "surveyor_name": row.surveyor_name,
        "surveyor_id": row.surveyor_id,
        "mobile": row.mobile,
        "email": row.email
    }


def authenticate_user(username: str, password: str):
    user = get_user(username,password)
    if not user:
        return False
    return user

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
    ):
    to_encode = data.copy()

    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=60)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    
def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token expired or invalid"
        )