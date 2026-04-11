"""
Pydantic models for course-related data.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Course schemas
class CourseBase(BaseModel):
    """Base course schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    source: str = Field(..., description="Source of the course content, e.g., 'fastbook', 'llm_from_scratch'")
    is_active: bool = Field(default=True)
    language: str = Field(default="en", max_length=10)


class CourseCreate(CourseBase):
    """Schema for creating a new course."""
    pass


class CourseUpdate(BaseModel):
    """Schema for updating an existing course."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None
    language: Optional[str] = Field(None, max_length=10)


class Course(CourseBase):
    """Schema for returning a course."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Chapter schemas
class ChapterBase(BaseModel):
    """Base chapter schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    chapter_number: int = Field(..., ge=1)
    is_active: bool = Field(default=True)


class ChapterCreate(ChapterBase):
    """Schema for creating a new chapter."""
    course_id: UUID


class ChapterUpdate(BaseModel):
    """Schema for updating an existing chapter."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    chapter_number: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class Chapter(ChapterBase):
    """Schema for returning a chapter."""
    id: UUID
    course_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChapterWithCourse(Chapter):
    """Chapter schema with course information."""
    course: Course


# Notebook schemas
class NotebookBase(BaseModel):
    """Base notebook schema."""
    title: str = Field(..., min_length=1, max_length=200)
    notebook_path: str = Field(..., description="Path to the notebook file relative to source")
    content: Optional[str] = Field(None, description="Notebook content (markdown/code)")
    language: str = Field(default="python", description="Programming language, e.g., 'python', 'markdown'")
    is_active: bool = Field(default=True)


class NotebookCreate(NotebookBase):
    """Schema for creating a new notebook."""
    chapter_id: UUID


class NotebookUpdate(BaseModel):
    """Schema for updating an existing notebook."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    notebook_path: Optional[str] = None
    content: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


class Notebook(NotebookBase):
    """Schema for returning a notebook."""
    id: UUID
    chapter_id: UUID
    content_hash: Optional[str] = Field(None, description="SHA256 hash of content for change detection")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NotebookWithChapter(Notebook):
    """Notebook schema with chapter information."""
    chapter: Chapter


# Composite schemas
class CourseWithChapters(Course):
    """Course schema with nested chapters."""
    chapters: List[Chapter] = []


class ChapterWithNotebooks(Chapter):
    """Chapter schema with nested notebooks."""
    notebooks: List[Notebook] = []


class CourseFull(Course):
    """Full course schema with chapters and notebooks."""
    chapters: List[ChapterWithNotebooks] = []