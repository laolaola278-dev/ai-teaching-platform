"""API endpoints for course content (skeleton)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.course import Course, CourseCreate, CourseUpdate
from app.api.v1.dependencies.auth import get_current_user, require_role
from app.services.course_service import CourseService

router = APIRouter()


class CourseQuery(BaseModel):
    course_id: str | None = None
    chapter_id: str | None = None


@router.get("/")
async def get_courses(query: CourseQuery = None):  # pragma: no cover
    return {"courses": []}


@router.post("/", response_model=Course, status_code=201)
async def create_course(
    course: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _admin: bool = Depends(require_role("admin")),
) -> Course:
    service = CourseService(db)
    return await service.create_course(course)


@router.put("/{course_id}", response_model=Course)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _admin: bool = Depends(require_role("admin")),
) -> Course:
    service = CourseService(db)
    updated_course = await service.update_course(course_id, course_update)
    if not updated_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated_course


@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _admin: bool = Depends(require_role("admin")),
) -> None:
    service = CourseService(db)
    success = await service.delete_course(course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")


@router.get("/{course_id}", response_model=Course)
async def get_course(course_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single course by ID."""
    service = CourseService(db)
    course = await service.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
