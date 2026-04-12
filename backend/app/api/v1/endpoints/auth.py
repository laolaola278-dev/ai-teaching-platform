"""Authentication endpoints (login/refresh)."""
from __future__ import annotations

from datetime import timedelta
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.services.user_service import UserService
from app.schemas.user import User as UserModel
from app.schemas.user import UserCreate

# Router
router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    service = UserService(db)
    user: UserModel | None = await service.get_by_username(req.username)  # type: ignore
    if user is None or not verify_password(req.password, getattr(user, "hashed_password", "")):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    user_id = str(getattr(user, "id", ""))
    payload = {"sub": user_id, "username": getattr(user, "username", ""), "roles": getattr(user, "roles", [])}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload, timedelta(days=7))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    payload = None
    from app.core.security import decode_token
    payload = decode_token(req.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token = create_access_token({"sub": payload.get("sub"), "username": payload.get("username"), "roles": payload.get("roles", [])})
    refresh_token = create_refresh_token({"sub": payload.get("sub"), "username": payload.get("username"), "roles": payload.get("roles", [])}, timedelta(days=7))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
