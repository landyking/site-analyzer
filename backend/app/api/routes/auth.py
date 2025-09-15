from datetime import timedelta
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from app.core.config import settings
from app.core import security
import requests

from app.models import (
    LoginRequest,
    RegisterRequest,
    OidcInfoResp,
    OidcTokenRequest,
    PostLoginResp,
    BaseResp,
    Token,
    UserCreate,
    UserRole,
    UserStatus,
    UserPublic
)
from app import crud
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(tags=["Auth"])

@router.post("/user-login", response_model=Token, summary="Login with Local Users")
async def user_login(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.status == UserStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, user.role == UserRole.ADMIN, expires_delta=access_token_expires
        )
    )

@router.post("/user-info", response_model=UserPublic, summary="Get user information")
def get_user_info(current_user: CurrentUser) -> Any:
    return current_user


@router.post("/user-register", response_model=UserPublic, summary="Register a new user")
async def user_register(session: SessionDep,user_in: RegisterRequest):
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate(**user_in.model_dump(),provider="local", sub=user_in.email)
    user = crud.create_user(session=session, user_create=user_create)
    return user


@router.get("/oidc-info", response_model=OidcInfoResp, summary="Get OIDC Information")
async def get_oidc_info() -> OidcInfoResp:
    # Provide login URL for OIDC provider
    return OidcInfoResp(login_url="https://accounts.google.com/o/oauth2/v2/auth")


@router.post("/oidc-token", response_model=PostLoginResp, summary="Use code to get OIDC token")
async def get_oidc_token(session: SessionDep,payload: OidcTokenRequest) -> PostLoginResp:
    if not payload.code:
        raise HTTPException(status_code=400, detail="Code required")
    # print(settings.GOOGLE_CLIENT_ID, settings.GOOGLE_CLIENT_SECRET)
    # print("Received OIDC code:", payload.code)
    # 1) Exchange authorization code for tokens
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": payload.code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": "postmessage",  # matches @react-oauth/google 'auth-code' flow
            "grant_type": "authorization_code",
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=10,
    )
    if token_resp.status_code != 200:
        print("Token response error:", token_resp.text)
        raise HTTPException(status_code=400, detail="Failed to exchange code")

    token_json = token_resp.json()
    id_token_str = token_json.get("id_token")
    if not id_token_str:
        raise HTTPException(status_code=400, detail="No id_token in response")

    # print("ID Token:", id_token_str)
    # decode jwt 
    
    try:
        idinfo = jwt.decode(id_token_str, options={"verify_signature": False})
    except Exception as e:
        print("Failed to decode ID token:", e)
        raise HTTPException(status_code=400, detail="Invalid ID token")

    email = idinfo.get("email")
    sub = idinfo.get("sub")
    email_verified = idinfo.get("email_verified", False)
    if not email or not sub or not email_verified:
        raise HTTPException(status_code=400, detail="Google user not verified")

    # 3) Find or create local user
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        # Create a local account for this Google user (random password just to satisfy schema)
        user_create = UserCreate(
            email=email,
            password="#########",
            provider="google",
            sub=sub,
        )
        user = crud.create_user(session=session, user_create=user_create)

    # 4) Issue your app's JWT
    # Update last_login for this user
    try:
        user = crud.touch_last_login(session=session, user=user)
    except Exception:
        # Non-fatal
        pass

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, user.role == UserRole.ADMIN, expires_delta=access_token_expires
    )

    return PostLoginResp(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        refresh_token=token_json.get("refresh_token"),
        error=0,
    )


@router.post("/user/token-refresh", response_model=PostLoginResp, summary="Refresh user token")
async def user_token_refresh() -> PostLoginResp:
    return PostLoginResp(access_token="refreshed", refresh_token="dummy", token_type="bearer", expires_in=3600, error=0)


@router.post("/user/logout", response_model=BaseResp, summary="Logout user")
async def user_logout():
    return BaseResp(error=0)
