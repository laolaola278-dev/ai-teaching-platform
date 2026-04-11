"""
SQLAlchemy models for user, role, permission, and progress tracking.
"""
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.course import Course


# Association table for many-to-many relationship between users and roles
user_role = Table(
    "user_role",
    BaseModel.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for many-to-many relationship between roles and permissions
role_permission = Table(
    "role_permission",
    BaseModel.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class User(BaseModel, TimestampMixin):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    # Columns
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role", 
        secondary=user_role,
        back_populates="users",
    )
    course_progress: Mapped[list["UserCourseProgress"]] = relationship(
        "UserCourseProgress", 
        back_populates="user",
        cascade="all, delete-orphan",
    )
    training_jobs: Mapped[list["TrainingJob"]] = relationship(
        "TrainingJob", 
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"


class Role(BaseModel, TimestampMixin):
    """Role model for grouping permissions."""
    
    __tablename__ = "roles"
    
    # Columns
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User", 
        secondary=user_role,
        back_populates="roles",
    )
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission", 
        secondary=role_permission,
        back_populates="roles",
    )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"


class Permission(BaseModel):
    """Permission model for fine-grained access control."""
    
    __tablename__ = "permissions"
    
    # Columns
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role", 
        secondary=role_permission,
        back_populates="permissions",
    )
    
    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name='{self.name}')>"


class UserCourseProgress(BaseModel, TimestampMixin):
    """Tracks user progress through courses."""
    
    __tablename__ = "user_course_progress"
    
    # Columns
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    progress_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_chapters: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_chapters: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_accessed_at: Mapped[str] = mapped_column(String, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="course_progress")
    course: Mapped["Course"] = relationship("Course", back_populates="user_progress")
    
    def __repr__(self) -> str:
        return f"<UserCourseProgress(user_id={self.user_id}, course_id={self.course_id}, progress={self.progress_percentage}%)>"