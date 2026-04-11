"""
Repository for user-related database operations.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, Role, Permission, UserCourseProgress
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user entities."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_with_roles(self, user_id: UUID) -> Optional[User]:
        """Get a user with their roles."""
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles))
        )
        return result.scalar_one_or_none()
    
    async def get_user_progress(self, user_id: UUID, course_id: UUID) -> Optional[UserCourseProgress]:
        """Get a user's progress for a specific course."""
        result = await self.db.execute(
            select(UserCourseProgress)
            .where(
                UserCourseProgress.user_id == user_id,
                UserCourseProgress.course_id == course_id,
            )
        )
        return result.scalar_one_or_none()
    
    async def update_user_progress(
        self, 
        user_id: UUID, 
        course_id: UUID, 
        progress_percentage: int,
        completed_chapters: int,
        total_chapters: int,
    ) -> Optional[UserCourseProgress]:
        """Update or create user progress for a course."""
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        from sqlalchemy import update as sql_update
        
        # Try to update existing record
        stmt = (
            sql_update(UserCourseProgress)
            .where(
                UserCourseProgress.user_id == user_id,
                UserCourseProgress.course_id == course_id,
            )
            .values(
                progress_percentage=progress_percentage,
                completed_chapters=completed_chapters,
                total_chapters=total_chapters,
            )
            .returning(UserCourseProgress)
        )
        
        result = await self.db.execute(stmt)
        updated = result.scalar_one_or_none()
        
        if updated:
            await self.db.commit()
            return updated
        
        # If no record exists, create one
        insert_stmt = pg_insert(UserCourseProgress).values(
            user_id=user_id,
            course_id=course_id,
            progress_percentage=progress_percentage,
            completed_chapters=completed_chapters,
            total_chapters=total_chapters,
        ).on_conflict_do_update(
            index_elements=["user_id", "course_id"],
            set_=dict(
                progress_percentage=progress_percentage,
                completed_chapters=completed_chapters,
                total_chapters=total_chapters,
            )
        ).returning(UserCourseProgress)
        
        result = await self.db.execute(insert_stmt)
        await self.db.commit()
        return result.scalar_one_or_none()
    
    async def get_active_users(self) -> List[User]:
        """Get all active users."""
        result = await self.db.execute(
            select(User)
            .where(User.is_active == True)
            .order_by(User.created_at)
        )
        return result.scalars().all()
    
    async def search_users(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """Search users by username, email, or full name."""
        from sqlalchemy import or_
        
        search_query = select(User).where(
            or_(
                User.username.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%"),
                User.full_name.ilike(f"%{query}%"),
            )
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(search_query)
        return result.scalars().all()