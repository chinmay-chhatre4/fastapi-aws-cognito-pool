from pydantic import BaseModel, EmailStr
from typing import Optional


class SignUpRequest(BaseModel):
    username: str
    password: str
    email: EmailStr


class ConfirmSignUpRequest(BaseModel):
    username: str
    code: str


class SignInRequest(BaseModel):
    username: str
    password: str


class ForgotPasswordRequest(BaseModel):
    username: str


class ConfirmForgotPasswordRequest(BaseModel):
    username: str
    code: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    previous_password: str
    proposed_password: str


class TokenResponse(BaseModel):
    access_token: Optional[str]
    id_token: Optional[str]
    refresh_token: Optional[str]
    token_type: Optional[str]
