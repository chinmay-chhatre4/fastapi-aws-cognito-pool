from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.auth import (
    SignUpRequest,
    ConfirmSignUpRequest,
    SignInRequest,
    ForgotPasswordRequest,
    ConfirmForgotPasswordRequest,
    ChangePasswordRequest,
    TokenResponse,
)
from app.deps import get_settings, get_cognito_service
from botocore.exceptions import ClientError

router = APIRouter()


# Create HTTPBearer instance for authentication
security = HTTPBearer()

@router.post("/register", status_code=201)
def register(data: SignUpRequest, settings=Depends(get_settings), cognito=Depends(get_cognito_service)):
    try:
        resp = cognito.sign_up(data.username, data.password, data.email)
        return {"user_sub": resp.get("UserSub")}
    except ClientError as e:
        raise HTTPException(status_code=400, detail=e.response.get("Error", {}).get("Message"))


@router.post("/confirm")
def confirm(data: ConfirmSignUpRequest, cognito=Depends(get_cognito_service)):
    try:
        cognito.confirm_sign_up(data.username, data.code)
        return {"success": True}
    except ClientError as e:
        raise HTTPException(status_code=400, detail=e.response.get("Error", {}).get("Message"))


@router.post("/signin", response_model=TokenResponse)
def signin(data: SignInRequest, cognito=Depends(get_cognito_service)):
    try:
        resp = cognito.initiate_auth(data.username, data.password)
        auth_result = resp.get("AuthenticationResult", {})
        return TokenResponse(
            access_token=auth_result.get("AccessToken"),
            id_token=auth_result.get("IdToken"),
            refresh_token=auth_result.get("RefreshToken"),
            token_type=auth_result.get("TokenType"),
        )
    except ClientError as e:
        raise HTTPException(status_code=401, detail=e.response.get("Error", {}).get("Message"))


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, cognito=Depends(get_cognito_service)):
    try:
        cognito.forgot_password(data.username)
        return {"success": True}
    except ClientError as e:
        raise HTTPException(status_code=400, detail=e.response.get("Error", {}).get("Message"))


@router.post("/confirm-forgot-password")
def confirm_forgot(data: ConfirmForgotPasswordRequest, cognito=Depends(get_cognito_service)):
    try:
        cognito.confirm_forgot_password(data.username, data.code, data.new_password)
        return {"success": True}
    except ClientError as e:
        raise HTTPException(status_code=400, detail=e.response.get("Error", {}).get("Message"))


@router.post("/change-password")
def change_password(data: ChangePasswordRequest,  credentials: HTTPAuthorizationCredentials = Depends(security), cognito=Depends(get_cognito_service)):
    # Extract the token from credentials
    token = credentials.credentials
    try:
        cognito.change_password(token, data.previous_password, data.proposed_password)
        return {"success": True}
    except ClientError as e:
        raise HTTPException(status_code=400, detail=e.response.get("Error", {}).get("Message"))


@router.post("/signout")
# def signout(Authorization: str = Header(..., alias="Authorization"), cognito=Depends(get_cognito_service)):
def signout(credentials: HTTPAuthorizationCredentials = Depends(security), cognito=Depends(get_cognito_service)):
     # Extract the token from credentials
    token = credentials.credentials
    try:
        cognito.global_sign_out(token)
        return {"success": True}
    except ClientError as e:
        raise HTTPException(status_code=400, detail=e.response.get("Error", {}).get("Message"))
