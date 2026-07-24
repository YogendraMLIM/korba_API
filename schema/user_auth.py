from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    surveyor_name: str
    surveyor_id: str
    email: str
    mobile: str
    zone: str
    ward: str


class UserSync(BaseModel):
    id: int | None = None
    username: str
    password: str | None = None
    ward: str | None = None
    zone: str | None = None
    surveyor_name: str | None = None
    surveyor_id: str | None = None
    mobile: str | None = None
    email: str | None = None
    access_token: str | None = None
    token_type: str | None = None
    refresh_token: str | None = None
    token_expiry: datetime | None = None
    is_logged_in: bool | int | None = None
    last_login: datetime | None = None


class UserLogout(BaseModel):
    username: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str
