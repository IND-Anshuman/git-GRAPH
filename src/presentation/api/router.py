from fastapi import APIRouter
from src.presentation.api.health import health_router
from src.presentation.api.repositories import repository_router
from src.presentation.api.entities import entity_router
from src.presentation.api.relationships import relationship_router
from src.presentation.api.temporal import temporal_router
from src.presentation.api.temporal_diagnostics import diagnostics_router
from src.presentation.api.logic import logic_router
from src.presentation.api.concepts import concepts_router
from src.presentation.api.meta_ontology import meta_router
from src.presentation.api.capabilities import capabilities_router
from src.presentation.api.reasoning import reasoning_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(repository_router)
api_router.include_router(entity_router)
api_router.include_router(relationship_router)
api_router.include_router(temporal_router)
api_router.include_router(diagnostics_router)
api_router.include_router(logic_router)
api_router.include_router(concepts_router)
api_router.include_router(meta_router)
api_router.include_router(capabilities_router)
api_router.include_router(reasoning_router)


