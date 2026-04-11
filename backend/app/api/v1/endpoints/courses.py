"""API endpoints for course content (skeleton)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.course import Course
from app.services.course_service import CourseService

router = APIRouter()


class CourseQuery(BaseModel):
    course_id: str | None = None
    chapter_id: str | None = None


@router.get("/")
async def get_courses(query: CourseQuery = None):  # pragma: no cover
    return {"courses": []}


@router.get("/{course_id}", response_model=Course)
async def get_course(course_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single course by ID."""
    service = CourseService(db)
    course = await service.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
