"""Main version 1 API router that collects all endpoints."""
from fastapi import APIRouter

# Import all v1 endpoints
from app.api.v1.endpoints import health, courses, users, algorithms, auth, notebooks

api_router = APIRouter()

# Health
api_router.include_router(health.router, tags=["health"])
# Courses
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
# Users
api_router.include_router(users.router, prefix="/users", tags=["users"])
# Algorithms
api_router.include_router(algorithms.router, prefix="/algorithms", tags=["algorithms"])
# Notebooks (protected write endpoints)
api_router.include_router(notebooks.router, prefix="/notebooks", tags=["notebooks"])
# Auth
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
