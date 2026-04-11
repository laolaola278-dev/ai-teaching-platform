"""
Health check endpoints for monitoring and load balancers.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "ai-teaching-platform",
        "timestamp": "2024-01-01T00:00:00Z",  # TODO: Use actual timestamp
    }


@router.get("/health/db")
async def database_health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """Database health check."""
    try:
        # Try to execute a simple query
        result = await db.execute("SELECT 1")
        result.scalar()
        
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }