"""
Main Application Entry Point.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from src.config import settings
from src.core.logging import setup_logging
from src.core.telemetry import setup_telemetry
from src.presentation.api.router import api_router
from src.container import Container

# Set up structured logging before anything else
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and shutdown lifecycle events."""
    logger.info("Starting up Temporal Code Knowledge Graph platform...")
    
    # Initialize container and bind to app state
    container = Container(settings)
    app.state.container = container
    
    # Initialize pattern registry from DB
    try:
        container.ontology_registry_service.initialize_registry()
        logger.info("Initialized pattern registry from database.")
    except Exception as e:
        logger.error(f"Failed to initialize pattern registry on startup: {e}")
    
    # DB Init
    # try:
    #     from src.infrastructure.database.models import Base
    #     Base.metadata.create_all(bind=container.engine)
    # except Exception as e:
    #     logger.error(f"Error initializing DB: {e}")
    
    yield
    
    logger.info("Shutting down Temporal Code Knowledge Graph platform...")
    container.engine.dispose()

def create_app() -> FastAPI:
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
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    )

    app.include_router(api_router)
    
    return app

app = create_app()
