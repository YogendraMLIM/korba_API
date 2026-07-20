from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    surveyor_name: str
    email: EmailStr
    mobile: str
    zone: str
    ward: str