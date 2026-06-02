from fastapi import APIRouter
from src.presentation.api.health import health_router
from src.presentation.api.repositories import repository_router
from src.presentation.api.entities import entity_router
from src.presentation.api.relationships import relationship_router
from src.presentation.api.temporal import temporal_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(repository_router)
api_router.include_router(entity_router)
api_router.include_router(relationship_router)
api_router.include_router(temporal_router)
