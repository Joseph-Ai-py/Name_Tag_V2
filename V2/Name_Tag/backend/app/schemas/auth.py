from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class AuthUserResponse(BaseModel):
    id: str
    email: EmailStr


class AuthResponse(BaseModel):
    user: AuthUserResponse
