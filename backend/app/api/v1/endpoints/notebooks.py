"""Notebook endpoints (skeleton) with admin-protected write operations."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.dependencies.auth import get_current_user, require_role
from app.schemas.course import NotebookCreate, NotebookUpdate, Notebook
from app.services.course_service import CourseService  # using course service for notebook ops as skeleton

router = APIRouter()


@router.post("/", response_model=Notebook, status_code=201)
async def create_notebook(notebook: NotebookCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user), _admin: bool = Depends(require_role("admin"))) -> Notebook:
    service = CourseService(db)
    return await service.create_notebook(notebook)


@router.get("/{notebook_id}", response_model=Notebook)
async def get_notebook(notebook_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)) -> Notebook:
    service = CourseService(db)
    nb = await service.get_notebook(notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return nb


@router.put("/{notebook_id}", response_model=Notebook)
async def update_notebook(notebook_id: str, notebook_update: NotebookUpdate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user), _admin: bool = Depends(require_role("admin"))) -> Notebook:
    service = CourseService(db)
    updated = await service.update_notebook(notebook_id, notebook_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return updated


@router.delete("/{notebook_id}")
async def delete_notebook(notebook_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user), _admin: bool = Depends(require_role("admin"))) -> None:
    service = CourseService(db)
    ok = await service.delete_notebook(notebook_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Notebook not found")
