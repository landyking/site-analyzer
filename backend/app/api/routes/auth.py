from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.models import (
    LoginRequest,
    RegisterRequest,
    OidcInfoResp,
    OidcTokenRequest,
    PostLoginResp,
    BaseResp,
)

router = APIRouter(prefix="/v1", tags=["Auth"])


@router.post("/user-login", response_model=PostLoginResp, summary="Login with Local Users")
async def user_login(payload: LoginRequest) -> PostLoginResp:
    # Placeholder logic; replace with real authentication
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return PostLoginResp(access_token="dummy", refresh_token="dummy", token_type="bearer", expires_in=3600, error=0)


@router.post("/user-register", response_model=BaseResp, summary="Register a new user")
async def user_register(payload: RegisterRequest):
    if payload.password != payload.password2:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    return BaseResp(error=0)


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
