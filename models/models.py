from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    username: str = "user1"
    password: str = "pass1"


class Token(BaseModel):
    username: str
    ward: str | None = None
    zone: str | None = None
    surveyor_name: str | None = None
    surveyor_id: str | None = None
    mobile: str | None = None
    email: str | None = None
    access_token: str
    token_type: str
    
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