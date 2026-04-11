"""
Main API router that includes all version 1 endpoints.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, courses, users, algorithms

api_router = APIRouter()

# Include routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(algorithms.router, prefix="/algorithms", tags=["algorithms"])