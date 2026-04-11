"""
Service layer for course management business logic.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course as CourseModel
from app.repositories.course_repository import CourseRepository
from app.schemas.course import CourseCreate, CourseUpdate


class CourseService:
    """Service for handling course-related operations."""
    
    def __init__(self, db: AsyncSession):
        self.repository = CourseRepository(db)
    
    async def get_courses(self, skip: int = 0, limit: int = 100) -> List[CourseModel]:
        """Get a list of courses with pagination."""
        return await self.repository.get_all(skip=skip, limit=limit)
    
    async def get_course(self, course_id: UUID) -> Optional[CourseModel]:
        """Get a specific course by ID."""
        return await self.repository.get_by_id(course_id)
    
    async def create_course(self, course_create: CourseCreate) -> CourseModel:
        """Create a new course."""
        course_data = course_create.model_dump()
        return await self.repository.create(course_data)
    
    async def update_course(
        self, 
        course_id: UUID, 
        course_update: CourseUpdate
    ) -> Optional[CourseModel]:
        """Update an existing course."""
        update_data = course_update.model_dump(exclude_unset=True)
        return await self.repository.update(course_id, update_data)
    
    async def delete_course(self, course_id: UUID) -> bool:
        """Delete a course."""
        return await self.repository.delete(course_id)
    
    async def get_course_with_chapters(self, course_id: UUID) -> Optional[CourseModel]:
        """Get a course with its chapters."""
        return await self.repository.get_with_chapters(course_id)
    
    async def search_courses(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[CourseModel]:
        """Search courses by title or description."""
        return await self.repository.search(query, skip=skip, limit=limit)