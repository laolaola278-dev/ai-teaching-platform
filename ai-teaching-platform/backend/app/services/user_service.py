"""
Service layer for user management and authentication.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User as UserModel
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service for handling user-related operations."""
    
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        """Get a list of users with pagination."""
        return await self.repository.get_all(skip=skip, limit=limit)
    
    async def get_user(self, user_id: UUID) -> Optional[UserModel]:
        """Get a specific user by ID."""
        return await self.repository.get_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by email address."""
        return await self.repository.get_by_email(email)
    
    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """Get a user by username."""
        return await self.repository.get_by_username(username)
    
    async def create_user(self, user_create: UserCreate) -> UserModel:
        """Create a new user."""
        # Hash password before storing
        from app.core.security import get_password_hash
        
        user_data = user_create.model_dump()
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        
        return await self.repository.create(user_data)
    
    async def update_user(
        self, 
        user_id: UUID, 
        user_update: UserUpdate
    ) -> Optional[UserModel]:
        """Update an existing user."""
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Hash new password if provided
        if "password" in update_data:
            from app.core.security import get_password_hash
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        return await self.repository.update(user_id, update_data)
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user."""
        return await self.repository.delete(user_id)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[UserModel]:
        """Authenticate a user with username and password."""
        from app.core.security import verify_password
        
        user = await self.get_user_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def change_password(
        self, 
        user_id: UUID, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Change user password after verifying current password."""
        from app.core.security import verify_password, get_password_hash
        
        user = await self.get_user(user_id)
        if not user:
            return False
        
        if not verify_password(current_password, user.hashed_password):
            return False
        
        new_hashed_password = get_password_hash(new_password)
        await self.repository.update(user_id, {"hashed_password": new_hashed_password})
        return True