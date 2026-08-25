import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status

from models.user import User
from security import verify_password


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def authenticate_user(user: User | None, password: str):
    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )