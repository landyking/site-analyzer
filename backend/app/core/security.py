import base64
import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(subject: int | Any, admin: bool, expires_delta: timedelta) -> str:
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "admin": admin}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def gen_tile_signature(user: int, task: int, exp: int) -> str:
    # Create a message string
    message = f"{user}:{task}:{exp}".encode()
    # Use SECRET_KEY as bytes
    key = settings.SECRET_KEY.encode()
    # HMAC-SHA256
    signature = hmac.new(key, message, hashlib.sha256).digest()
    # URL-safe base64 encode, remove trailing '=' for compactness
    return base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
