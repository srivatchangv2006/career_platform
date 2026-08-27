from enum import Enum

from pydantic import BaseModel, EmailStr


class RegistrationRole(str, Enum):
    CANDIDATE = "CANDIDATE"
    RECRUITER = "RECRUITER"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: RegistrationRole = RegistrationRole.CANDIDATE


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    status: str