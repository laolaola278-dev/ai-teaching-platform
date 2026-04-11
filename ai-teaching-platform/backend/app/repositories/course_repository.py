"""
Repository for course-related database operations.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course, Chapter, Notebook
from app.repositories.base_repository import BaseRepository


class CourseRepository(BaseRepository[Course]):
    """Repository for course entities."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Course, db)
    
    async def get_with_chapters(self, course_id: UUID) -> Optional[Course]:
        """Get a course with its chapters."""
        result = await self.db.execute(
            select(Course)
            .where(Course.id == course_id)
            .options(selectinload(Course.chapters))
        )
        return result.scalar_one_or_none()
    
    async def get_with_chapters_and_notebooks(self, course_id: UUID) -> Optional[Course]:
        """Get a course with chapters and notebooks."""
        result = await self.db.execute(
            select(Course)
            .where(Course.id == course_id)
            .options(
                selectinload(Course.chapters)
                .selectinload(Chapter.notebooks)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_source(self, source: str) -> List[Course]:
        """Get all courses from a specific source."""
        result = await self.db.execute(
            select(Course)
            .where(Course.source == source)
            .order_by(Course.created_at)
        )
        return result.scalars().all()
    
    async def get_chapter_with_notebooks(self, chapter_id: UUID) -> Optional[Chapter]:
        """Get a chapter with its notebooks."""
        result = await self.db.execute(
            select(Chapter)
            .where(Chapter.id == chapter_id)
            .options(selectinload(Chapter.notebooks))
        )
        return result.scalar_one_or_none()
    
    async def get_notebook_by_path(self, notebook_path: str) -> Optional[Notebook]:
        """Get a notebook by its path."""
        result = await self.db.execute(
            select(Notebook)
            .where(Notebook.notebook_path == notebook_path)
        )
        return result.scalar_one_or_none()
    
    async def search_courses(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Course]:
        """Search courses by title or description."""
        from sqlalchemy import or_
        
        search_query = select(Course).where(
            or_(
                Course.title.ilike(f"%{query}%"),
                Course.description.ilike(f"%{query}%"),
            )
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(search_query)
        return result.scalars().all()
    
    async def get_courses_by_language(self, language: str) -> List[Course]:
        """Get all courses in a specific language."""
        result = await self.db.execute(
            select(Course)
            .where(Course.language == language)
            .order_by(Course.created_at)
        )
        return result.scalars().all()