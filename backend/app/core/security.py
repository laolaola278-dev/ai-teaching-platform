"""Security utilities: password hashing and JWT token handling."""
from __future__ import annotations

import datetime
import os
from datetime import timedelta

from passlib.context import CryptContext
from jose import JWTError, jwt

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


# JWT configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "CHANGE_ME_SECRET")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
AUDIENCE = os.environ.get("AUDIENCE")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))


def _create_token(data: dict, expires_delta: datetime.timedelta | None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None) -> str:
    return _create_token(data, expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(data: dict, expires_delta: datetime.timedelta | None = None) -> str:
    return _create_token(data, expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))


def decode_token(token: str) -> dict | None:
    try:
        if AUDIENCE:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=AUDIENCE)
        else:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
