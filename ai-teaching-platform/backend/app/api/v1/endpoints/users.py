"""
User management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.core.security import hash_password
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=List[User])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> List[User]:
    """List all users with pagination."""
    service = UserService(db)
    users = await service.get_users(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get a specific user by ID."""
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=User, status_code=201)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Create a new user."""
    service = UserService(db)
    data = user.dict()
    if "password" in data and data["password"]:
        data["password"] = hash_password(data["password"])
    # Rebuild the Pydantic model with hashed password if needed
    user_hashed = UserCreate(**data) if "password" in data else user
    return await service.create_user(user_hashed)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update an existing user."""
    service = UserService(db)
    updated_user = await service.update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a user."""
    service = UserService(db)
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
