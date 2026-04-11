"""
SQLAlchemy models for course, chapter, and notebook entities.
"""
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import UserCourseProgress


class Course(BaseModel, TimestampMixin):
    """Course model representing a collection of chapters."""
    
    __tablename__ = "courses"
    
    # Columns
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="custom")
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Relationships
    chapters: Mapped[list["Chapter"]] = relationship(
        "Chapter", 
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Chapter.chapter_number",
    )
    user_progress: Mapped[list["UserCourseProgress"]] = relationship(
        "UserCourseProgress", 
        back_populates="course",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Course(id={self.id}, title='{self.title}')>"


class Chapter(BaseModel, TimestampMixin):
    """Chapter model representing a section within a course."""
    
    __tablename__ = "chapters"
    
    # Columns
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="chapters")
    notebooks: Mapped[list["Notebook"]] = relationship(
        "Notebook", 
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="Notebook.created_at",
    )
    
    def __repr__(self) -> str:
        return f"<Chapter(id={self.id}, title='{self.title}', course_id={self.course_id})>"


class Notebook(BaseModel, TimestampMixin):
    """Notebook model representing educational content."""
    
    __tablename__ = "notebooks"
    
    # Columns
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    notebook_path: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="python")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    chapter_id: Mapped[str] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Relationships
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="notebooks")
    
    def __repr__(self) -> str:
        return f"<Notebook(id={self.id}, title='{self.title}', chapter_id={self.chapter_id})>"