"""
Course-related API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.schemas.course import Course, CourseCreate, CourseUpdate
from app.services.course_service import CourseService

router = APIRouter()


@router.get("/", response_model=List[Course])
async def list_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> List[Course]:
    """List all courses with pagination."""
    service = CourseService(db)
    courses = await service.get_courses(skip=skip, limit=limit)
    return courses


@router.get("/{course_id}", response_model=Course)
async def get_course(
    course_id: str,
    db: AsyncSession = Depends(get_db),
) -> Course:
    """Get a specific course by ID."""
    service = CourseService(db)
    course = await service.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/", response_model=Course, status_code=201)
async def create_course(
    course: CourseCreate,
    db: AsyncSession = Depends(get_db),
) -> Course:
    """Create a new course."""
    service = CourseService(db)
    return await service.create_course(course)


@router.put("/{course_id}", response_model=Course)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    db: AsyncSession = Depends(get_db),
) -> Course:
    """Update an existing course."""
    service = CourseService(db)
    updated_course = await service.update_course(course_id, course_update)
    if not updated_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated_course


@router.delete("/{course_id}", status_code=204)
async def delete_course(
    course_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a course."""
    service = CourseService(db)
    success = await service.delete_course(course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")