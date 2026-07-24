from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class User(BaseModel):
    username: str = "user1"
    password: str = "pass1"


class Token(BaseModel):
    id: int
    username: str
    ward: str | None = None
    zone: str | None = None
    user_id: str | None = None
    surveyor_name: str | None = None
    surveyor_id: str | None = None
    mobile: str | None = None
    email: str | None = None
    access_token: str
    token_type: str
    refresh_token: str | None = None
    token_expiry: datetime | None = None
    is_logged_in: bool = False
    last_login: datetime | None = None
    
class WeatherRequest(BaseModel):
    district: str = ""
    circle: str = "AP"
    days: int = Field(
        default=7,
        ge=1,   # minimum value
        le=7    # maximum value
    )
    
class AccumRainfallRequest(BaseModel):
    district: str = ""
    circle: str = "AP"

class TokenData(BaseModel):
    username: Optional[str] = None
