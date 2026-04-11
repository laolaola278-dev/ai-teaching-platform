"""API router aggregator for v1 endpoints."""
from fastapi import APIRouter

from .endpoints import algorithms as algorithms_endpoint
from .endpoints import courses as courses_endpoint

api_router = APIRouter()

# Include sub-routers
api_router.include_router(algorithms_endpoint.router, prefix="/algorithms", tags=["algorithms"])
api_router.include_router(courses_endpoint.router, prefix="/courses", tags=["courses"])
