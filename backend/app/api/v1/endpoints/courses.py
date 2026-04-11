"""API endpoints for course content (skeleton)."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CourseQuery(BaseModel):
    course_id: str | None = None
    chapter_id: str | None = None


@router.get("/")
async def get_courses(query: CourseQuery = None):  # pragma: no cover
    return {"courses": []}
