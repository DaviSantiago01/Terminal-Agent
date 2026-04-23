from datetime import datetime

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: datetime


class LoginResponse(BaseModel):
    session_token: str
    expires_at: datetime
    user: UserResponse


class AuthMeResponse(BaseModel):
    user: UserResponse


class LogoutResponse(BaseModel):
    status: str
