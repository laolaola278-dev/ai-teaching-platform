import pytest
from app.services.course_service import CourseService


class FakeCourseRepository:
    def __init__(self, db):
        self.db = db
        self.courses = {}

    async def get_all(self, skip=0, limit=100):
        return list(self.courses.values())[skip:skip+limit]

    async def get_by_id(self, course_id):
        return self.courses.get(str(course_id))

    async def create(self, course_data):
        cid = str(len(self.courses) + 1)
        course = dict(course_data)
        course["id"] = cid
        self.courses[cid] = course
        return course

    async def update(self, course_id, update_data):
        c = self.courses.get(str(course_id))
        if not c:
            return None
        c.update(update_data)
        return c

    async def delete(self, course_id):
        if str(course_id) in self.courses:
            del self.courses[str(course_id)]
            return True
        return False

    async def get_with_chapters(self, course_id):
        return self.courses.get(str(course_id))

    async def search(self, query, skip=0, limit=100):
        return [c for c in self.courses.values() if query.lower() in (c.get("title","").lower())]


@pytest.mark.asyncio
async def test_course_crud_flow(monkeypatch):
    import app.repositories.course_repository as repo
    monkeypatch.setattr(repo, "CourseRepository", lambda db: FakeCourseRepository(db))
    service = CourseService(db=None)
    # Create
    from app.schemas.course import CourseCreate
    data = CourseCreate(title="Test Course", source="demo", language="en", is_active=True)
    created = await service.create_course(data)
    assert created["title"] == "Test Course"
    cid = created["id"]
    # Read
    course = await service.get_course(cid)
    assert course["id"] == cid
    # Update
    from app.schemas.course import CourseUpdate
    updated = await service.update_course(cid, CourseUpdate(title="Updated"))
    assert updated["title"] == "Updated"
    # Delete
    ok = await service.delete_course(cid)
    assert ok is True
