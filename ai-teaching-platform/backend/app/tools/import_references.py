"""
Script to import course content from reference repositories.
"""
import asyncio
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import nbformat
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.course import Course, Chapter, Notebook
from app.schemas.course import CourseCreate, ChapterCreate, NotebookCreate


class ReferenceImporter:
    """Import course content from reference repositories."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def import_all_references(self) -> Dict[str, int]:
        """Import all reference repositories."""
        results = {
            "courses_created": 0,
            "chapters_created": 0,
            "notebooks_created": 0,
        }
        
        # Import fastbook
        fastbook_path = Path("references/fastbook")
        if fastbook_path.exists():
            print(f"Importing fastbook from {fastbook_path}")
            fastbook_results = await self.import_fastbook(fastbook_path)
            results["courses_created"] += fastbook_results.get("courses_created", 0)
            results["chapters_created"] += fastbook_results.get("chapters_created", 0)
            results["notebooks_created"] += fastbook_results.get("notebooks_created", 0)
        
        # Import llm-from-scratch
        llm_path = Path("references/llm-from-scratch")
        if llm_path.exists():
            print(f"Importing llm-from-scratch from {llm_path}")
            llm_results = await self.import_llm_from_scratch(llm_path)
            results["courses_created"] += llm_results.get("courses_created", 0)
            results["chapters_created"] += llm_results.get("chapters_created", 0)
            results["notebooks_created"] += llm_results.get("notebooks_created", 0)
        
        return results
    
    async def import_fastbook(self, base_path: Path) -> Dict[str, int]:
        """Import fastbook Jupyter notebooks."""
        results = {
            "courses_created": 0,
            "chapters_created": 0,
            "notebooks_created": 0,
        }
        
        # Create fastbook course
        course_data = CourseCreate(
            title="Fastbook - Deep Learning for Coders",
            description="Practical deep learning for coders using fastai and PyTorch.",
            source="fastbook",
            language="en",
        )
        
        course = await self._create_course(course_data)
        if not course:
            print("Failed to create fastbook course")
            return results
        
        results["courses_created"] = 1
        
        # Find and process notebook files
        notebook_files = list(base_path.glob("*.ipynb"))
        
        # Group by chapter (using filename prefix)
        chapters: Dict[str, List[Path]] = {}
        for notebook_path in notebook_files:
            # Extract chapter number from filename (e.g., "01_intro.ipynb" -> "01")
            filename = notebook_path.stem
            if "_" in filename:
                chapter_prefix = filename.split("_")[0]
                if chapter_prefix.isdigit():
                    chapter_num = int(chapter_prefix)
                    if chapter_num not in chapters:
                        chapters[chapter_num] = []
                    chapters[chapter_num].append(notebook_path)
        
        # Create chapters and notebooks
        for chapter_num in sorted(chapters.keys()):
            # Create chapter
            chapter_title = f"Chapter {chapter_num}"
            if chapter_num == 0:
                chapter_title = "Introduction"
            
            chapter_data = ChapterCreate(
                title=chapter_title,
                description=f"Fastbook Chapter {chapter_num}",
                chapter_number=chapter_num,
                course_id=course.id,
            )
            
            chapter = await self._create_chapter(chapter_data)
            if not chapter:
                print(f"Failed to create chapter {chapter_num}")
                continue
            
            results["chapters_created"] += 1
            
            # Create notebooks for this chapter
            for notebook_path in chapters[chapter_num]:
                notebook_result = await self._create_notebook_from_ipynb(
                    notebook_path, chapter.id, chapter_num
                )
                if notebook_result:
                    results["notebooks_created"] += 1
        
        print(f"Imported fastbook: {results}")
        return results
    
    async def import_llm_from_scratch(self, base_path: Path) -> Dict[str, int]:
        """Import llm-from-scratch educational content."""
        results = {
            "courses_created": 0,
            "chapters_created": 0,
            "notebooks_created": 0,
        }
        
        # Create llm-from-scratch course
        course_data = CourseCreate(
            title="LLM from Scratch",
            description="Build Large Language Models from scratch with PyTorch.",
            source="llm_from_scratch",
            language="en",
        )
        
        course = await self._create_course(course_data)
        if not course:
            print("Failed to create llm-from-scratch course")
            return results
        
        results["courses_created"] = 1
        
        # Define module structure as chapters
        modules = [
            (1, "llm", "Core Transformer Implementation"),
            (2, "alignment", "Model Alignment (SFT & RL)"),
            (3, "data_processing", "Data Processing Pipeline"),
            (4, "kernel", "Kernel Optimizations"),
            (5, "parallel", "Parallel Training"),
            (6, "bench_mark", "Benchmarking"),
        ]
        
        for chapter_num, module_name, module_desc in modules:
            module_path = base_path / module_name
            
            if not module_path.exists():
                continue
            
            # Create chapter
            chapter_data = ChapterCreate(
                title=f"{module_name} - {module_desc}",
                description=f"LLM from Scratch: {module_desc}",
                chapter_number=chapter_num,
                course_id=course.id,
            )
            
            chapter = await self._create_chapter(chapter_data)
            if not chapter:
                print(f"Failed to create chapter {module_name}")
                continue
            
            results["chapters_created"] += 1
            
            # Find Python files in this module
            py_files = list(module_path.rglob("*.py"))
            
            # Create notebooks for each Python file
            for py_file in py_files:
                # Skip __init__.py and test files
                if py_file.name == "__init__.py" or "test" in py_file.name:
                    continue
                
                notebook_result = await self._create_notebook_from_py(
                    py_file, chapter.id, chapter_num
                )
                if notebook_result:
                    results["notebooks_created"] += 1
        
        # Also import README as a notebook
        readme_path = base_path / "README.md"
        if readme_path.exists():
            chapter_data = ChapterCreate(
                title="README - Project Overview",
                description="LLM from Scratch project overview and documentation",
                chapter_number=len(modules) + 1,
                course_id=course.id,
            )
            
            chapter = await self._create_chapter(chapter_data)
            if chapter:
                results["chapters_created"] += 1
                
                notebook_result = await self._create_notebook_from_markdown(
                    readme_path, chapter.id, chapter.chapter_number
                )
                if notebook_result:
                    results["notebooks_created"] += 1
        
        print(f"Imported llm-from-scratch: {results}")
        return results
    
    async def _create_course(self, course_data: CourseCreate) -> Optional[Course]:
        """Create a course in the database."""
        try:
            # Check if course already exists
            from sqlalchemy import select
            result = await self.db.execute(
                select(Course).where(
                    Course.title == course_data.title,
                    Course.source == course_data.source,
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"Course already exists: {course_data.title}")
                return existing
            
            # Create new course
            course = Course(**course_data.model_dump())
            self.db.add(course)
            await self.db.commit()
            await self.db.refresh(course)
            
            print(f"Created course: {course.title}")
            return course
            
        except Exception as e:
            print(f"Error creating course: {e}")
            await self.db.rollback()
            return None
    
    async def _create_chapter(self, chapter_data: ChapterCreate) -> Optional[Chapter]:
        """Create a chapter in the database."""
        try:
            # Check if chapter already exists
            from sqlalchemy import select
            result = await self.db.execute(
                select(Chapter).where(
                    Chapter.title == chapter_data.title,
                    Chapter.course_id == chapter_data.course_id,
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"Chapter already exists: {chapter_data.title}")
                return existing
            
            # Create new chapter
            chapter = Chapter(**chapter_data.model_dump())
            self.db.add(chapter)
            await self.db.commit()
            await self.db.refresh(chapter)
            
            print(f"Created chapter: {chapter.title}")
            return chapter
            
        except Exception as e:
            print(f"Error creating chapter: {e}")
            await self.db.rollback()
            return None
    
    async def _create_notebook_from_ipynb(
        self, 
        notebook_path: Path, 
        chapter_id: str,
        chapter_num: int
    ) -> Optional[Notebook]:
        """Create a notebook from Jupyter notebook file."""
        try:
            # Read notebook
            with open(notebook_path, "r", encoding="utf-8") as f:
                notebook_content = f.read()
            
            # Parse notebook to extract metadata
            try:
                nb = nbformat.reads(notebook_content, as_version=4)
                
                # Extract title from first markdown cell
                title = notebook_path.stem.replace("_", " ").title()
                for cell in nb.cells:
                    if cell.cell_type == "markdown" and cell.source.strip():
                        # Use first line as title
                        first_line = cell.source.strip().split("\n")[0]
                        if first_line.startswith("#"):
                            title = first_line.lstrip("#").strip()
                        break
                
                # Extract content preview
                content_preview = self._extract_notebook_preview(nb)
                
            except Exception as e:
                print(f"Error parsing notebook {notebook_path}: {e}")
                title = notebook_path.stem.replace("_", " ").title()
                content_preview = ""
            
            # Calculate content hash
            content_hash = hashlib.sha256(notebook_content.encode()).hexdigest()
            
            # Check if notebook already exists
            from sqlalchemy import select
            result = await self.db.execute(
                select(Notebook).where(Notebook.content_hash == content_hash)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"Notebook already exists: {title}")
                return existing
            
            # Create notebook
            notebook_data = NotebookCreate(
                title=title,
                notebook_path=str(notebook_path.relative_to("references")),
                content=content_preview[:5000],  # Limit preview size
                language="python",
                chapter_id=chapter_id,
            )
            
            notebook = Notebook(
                **notebook_data.model_dump(),
                content_hash=content_hash,
            )
            
            self.db.add(notebook)
            await self.db.commit()
            await self.db.refresh(notebook)
            
            print(f"Created notebook: {title}")
            return notebook
            
        except Exception as e:
            print(f"Error creating notebook from {notebook_path}: {e}")
            await self.db.rollback()
            return None
    
    async def _create_notebook_from_py(
        self, 
        py_path: Path, 
        chapter_id: str,
        chapter_num: int
    ) -> Optional[Notebook]:
        """Create a notebook from Python file."""
        try:
            # Read Python file
            with open(py_path, "r", encoding="utf-8") as f:
                py_content = f.read()
            
            # Extract title from filename
            title = py_path.stem.replace("_", " ").title()
            
            # Try to extract docstring as description
            content_preview = ""
            lines = py_content.split("\n")
            in_docstring = False
            docstring_lines = []
            
            for line in lines[:50]:  # Check first 50 lines
                stripped = line.strip()
                
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    if in_docstring:
                        # End of docstring
                        in_docstring = False
                        if docstring_lines:
                            content_preview = "\n".join(docstring_lines)
                        break
                    else:
                        # Start of docstring
                        in_docstring = True
                        docstring_content = stripped[3:-3] if len(stripped) > 6 else ""
                        if docstring_content:
                            docstring_lines.append(docstring_content)
                elif in_docstring:
                    docstring_lines.append(stripped)
            
            if not content_preview and docstring_lines:
                content_preview = "\n".join(docstring_lines)
            
            # Calculate content hash
            content_hash = hashlib.sha256(py_content.encode()).hexdigest()
            
            # Check if notebook already exists
            from sqlalchemy import select
            result = await self.db.execute(
                select(Notebook).where(Notebook.content_hash == content_hash)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"Python notebook already exists: {title}")
                return existing
            
            # Create notebook
            notebook_data = NotebookCreate(
                title=title,
                notebook_path=str(py_path.relative_to("references")),
                content=content_preview[:5000],
                language="python",
                chapter_id=chapter_id,
            )
            
            notebook = Notebook(
                **notebook_data.model_dump(),
                content_hash=content_hash,
            )
            
            self.db.add(notebook)
            await self.db.commit()
            await self.db.refresh(notebook)
            
            print(f"Created Python notebook: {title}")
            return notebook
            
        except Exception as e:
            print(f"Error creating notebook from {py_path}: {e}")
            await self.db.rollback()
            return None
    
    async def _create_notebook_from_markdown(
        self, 
        md_path: Path, 
        chapter_id: str,
        chapter_num: int
    ) -> Optional[Notebook]:
        """Create a notebook from Markdown file."""
        try:
            # Read Markdown file
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            
            # Extract title from first line
            title = md_path.stem.replace("_", " ").title()
            lines = md_content.split("\n")
            for line in lines:
                if line.startswith("# "):
                    title = line.lstrip("#").strip()
                    break
            
            # Use first 200 chars as preview
            content_preview = md_content[:2000]
            
            # Calculate content hash
            content_hash = hashlib.sha256(md_content.encode()).hexdigest()
            
            # Check if notebook already exists
            from sqlalchemy import select
            result = await self.db.execute(
                select(Notebook).where(Notebook.content_hash == content_hash)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"Markdown notebook already exists: {title}")
                return existing
            
            # Create notebook
            notebook_data = NotebookCreate(
                title=title,
                notebook_path=str(md_path.relative_to("references")),
                content=content_preview,
                language="markdown",
                chapter_id=chapter_id,
            )
            
            notebook = Notebook(
                **notebook_data.model_dump(),
                content_hash=content_hash,
            )
            
            self.db.add(notebook)
            await self.db.commit()
            await self.db.refresh(notebook)
            
            print(f"Created Markdown notebook: {title}")
            return notebook
            
        except Exception as e:
            print(f"Error creating notebook from {md_path}: {e}")
            await self.db.rollback()
            return None
    
    def _extract_notebook_preview(self, nb: nbformat.NotebookNode) -> str:
        """Extract a text preview from Jupyter notebook."""
        preview_parts = []
        
        for cell in nb.cells[:10]:  # First 10 cells
            if cell.cell_type == "markdown":
                preview_parts.append(cell.source[:500])  # Limit markdown preview
            elif cell.cell_type == "code":
                # Add code with limited lines
                code_lines = cell.source.split("\n")[:10]
                preview_parts.append("\n".join(code_lines))
        
        return "\n\n".join(preview_parts)


async def main():
    """Main import function."""
    print("Starting reference import...")
    
    # Create database engine
    engine = create_async_engine(str(settings.DATABASE_URL))
    
    async with AsyncSessionLocal() as db:
        importer = ReferenceImporter(db)
        results = await importer.import_all_references()
        
        print("\nImport completed:")
        print(f"  Courses created: {results['courses_created']}")
        print(f"  Chapters created: {results['chapters_created']}")
        print(f"  Notebooks created: {results['notebooks_created']}")
    
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())