from datetime import timedelta
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import settings
from app.core import security

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
async def get_oidc_token(payload: OidcTokenRequest) -> PostLoginResp:
    if not payload.code:
        raise HTTPException(status_code=400, detail="Code required")
    return PostLoginResp(access_token="oidc_dummy", refresh_token="dummy", token_type="bearer", expires_in=3600, error=0)


@router.post("/user/token-refresh", response_model=PostLoginResp, summary="Refresh user token")
async def user_token_refresh() -> PostLoginResp:
    return PostLoginResp(access_token="refreshed", refresh_token="dummy", token_type="bearer", expires_in=3600, error=0)


@router.post("/user/logout", response_model=BaseResp, summary="Logout user")
async def user_logout():
    return BaseResp(error=0)
