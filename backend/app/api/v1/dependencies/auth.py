"""Authentication dependencies for FastAPI routes."""
from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db
import os
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # If token is missing, treat as unauthorized
    if not token:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    payload = decode_token(token)  # may raise JWTError in decode_token, will be handled as 401 by tests
    # Optional issuer/audience checks to support boundary tests
    issuer_env = os.environ.get("ISSUER")
    if issuer_env and payload:
        if payload.get("iss") != issuer_env:
            raise HTTPException(status_code=401, detail="Invalid issuer")
    # Audience check (optional)
    aud_env = os.environ.get("AUDIENCE")
    if aud_env and payload:
        if payload.get("aud") != aud_env:
            raise HTTPException(status_code=401, detail="Invalid audience")
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    # Normalize to a simple user dict expected by tests/consumers
    user = {
        "id": str(payload.get("sub")),
        "username": payload.get("username"),
        "roles": payload.get("roles", payload.get("role", [])),
    }
    return user

def require_role(role: str):
    async def _dep(user: dict = Depends(get_current_user)):
        roles = user.get("roles", []) or []
        if role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return True
    return _dep
