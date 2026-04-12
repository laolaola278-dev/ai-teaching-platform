import asyncio
import uuid
import pytest

from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate


class FakeUserRepository:
    def __init__(self, db):
        self.db = db
        self.users = {}

    async def get_users(self, skip=0, limit=100):
        return list(self.users.values())[skip:skip+limit]

    async def get_by_id(self, user_id):
        return self.users.get(str(user_id))

    async def get_by_email(self, email):
        for u in self.users.values():
            if u.get("email") == email:
                return u
        return None

    async def get_by_username(self, username):
        for u in self.users.values():
            if u.get("username") == username:
                return u
        return None

    async def create(self, user_data):
        new_id = str(uuid.uuid4())
        user = dict(user_data)
        user["id"] = new_id
        self.users[new_id] = user
        return user

    async def update(self, user_id, update_data):
        uid = str(user_id)
        if uid not in self.users:
            return None
        self.users[uid].update(update_data)
        return self.users[uid]

    async def delete(self, user_id):
        uid = str(user_id)
        if uid in self.users:
            del self.users[uid]
            return True
        return False

    async def get_all(self, skip=0, limit=100):
        return await self.get_users(skip, limit)

    async def get_by_username_or_email(self, username):  # unused helper
        return await self.get_by_username(username)


@pytest.mark.asyncio
async def test_create_user_hashes_password_and_stores(monkeypatch):
    import app.repositories.user_repository as repo
    monkeypatch.setattr(repo, "UserRepository", lambda db: FakeUserRepository(db))
    # patch password hashing utilities
    monkeypatch.setattr("app.core.security.get_password_hash", lambda pw: "HASHED_" + pw)
    monkeypatch.setattr("app.core.security.verify_password", lambda pw, hashed: hashed == f"HASHED_{pw}")

    service = UserService(db=None)
    user_in = UserCreate(username="alice", email="alice@example.com", password="secret123", full_name="Alice")
    created = await service.create_user(user_in)
    assert created["username"] == "alice"
    assert created["hashed_password"] == "HASHED_secret123"


@pytest.mark.asyncio
async def test_authenticate_user_success_and_failure(monkeypatch):
    import app.repositories.user_repository as repo
    fake_repo = FakeUserRepository(None)
    # prepopulate a user
    hashed = "HASHED_secret123"
    user = {"id": str(uuid.uuid4()), "username": "bob", "email": "bob@example.com", "hashed_password": hashed, "full_name": "Bob", "is_active": True}
    fake_repo.users[user["id"]] = user
    monkeypatch.setattr(repo, "UserRepository", lambda db: fake_repo)
    monkeypatch.setattr("app.core.security.verify_password", lambda pw, h: h == f"HASHED_{pw}")
    service = UserService(db=None)
    auth_ok = await service.authenticate_user("bob", "secret123")
    assert auth_ok is not None
    auth_fail = await service.authenticate_user("bob", "wrong")
    assert auth_fail is None
