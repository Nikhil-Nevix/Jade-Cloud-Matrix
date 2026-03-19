from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"


class AuthResponse(BaseModel):
    user_id: int
    email: str
    role: str
    token: str
    expires_at: str


class ErrorResponse(BaseModel):
    error: str
    message: str
