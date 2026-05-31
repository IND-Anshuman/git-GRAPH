"""
Main Application Entry Point.
Aggregates and exposes the API routers from the bounded contexts.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from src.config import settings
from src.core.logging import setup_logging
from src.core.telemetry import setup_telemetry

# Set up structured logging before anything else
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and shutdown lifecycle events."""
    logger.info("Starting up Temporal Code Knowledge Graph platform...")
    # TODO: Initialize connection pools (Postgres, Redis, Vector Index) here.
    
    yield
    
    logger.info("Shutting down Temporal Code Knowledge Graph platform...")
    # TODO: Clean up connection pools here.


app = FastAPI(
    title="Temporal Code Knowledge Graph API",
    description="Production-grade AI-powered codebase analysis, evolution, and RAG API.",
    version="0.1.0",
    lifespan=lifespan,
)

# OpenTelemetry configuration
setup_telemetry(app)

# CORS middleware for user interface access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


# TODO: Register routers from bounded contexts:
# from src.contexts.ingestion.interface.api.router import router as ingestion_router
# from src.contexts.graph.interface.api.router import router as graph_router
# from src.contexts.retrieval.interface.api.router import router as retrieval_router
# from src.contexts.agentic.interface.api.router import router as agentic_router
#
# app.include_router(ingestion_router, prefix="/api/v1/ingestion", tags=["Ingestion"])
# app.include_router(graph_router, prefix="/api/v1/graph", tags=["Knowledge Graph"])
# app.include_router(retrieval_router, prefix="/api/v1/retrieval", tags=["RAG Retrieval"])
# app.include_router(agentic_router, prefix="/api/v1/agents", tags=["AI Agents"])
