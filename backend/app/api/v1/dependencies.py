"""API dependencies for FastAPI routes."""
from typing import AsyncGenerator, Optional

from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from app.core.database import async_session
except Exception:
    async_session = None  # Fallback for skeleton without full DB wiring


async def get_db() -> AsyncGenerator[Optional[AsyncSession], None]:  # pragma: no cover
    """Yield a database session if available; otherwise yield None."""
    if async_session is not None:
        async for session in async_session():  # type: ignore[attr-defined]
            yield session  # type: ignore
    else:
        yield None
