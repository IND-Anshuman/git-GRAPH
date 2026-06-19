"""API endpoints for Phase 7B Architectural Intelligence Layer."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from src.presentation.dependencies import (
    get_architecture_reasoning_engine,
    get_fitness_function_engine,
    get_invariant_reasoning_engine,
    get_drift_reasoning_engine,
    get_architecture_timeline_engine,
    get_architecture_benchmark_engine,
    get_architecture_similarity_engine,
    get_ownership_reasoning_engine,
    get_refactoring_reasoning_engine,
    get_architecture_recommendation_engine,
    get_bounded_context_engine,
    get_architecture_artifact_service
)
from src.application.architecture.architecture_reasoning_engine import ArchitectureReasoningEngine
from src.application.architecture.fitness_function_engine import FitnessFunctionEngine
from src.application.architecture.invariant_reasoning_engine import InvariantReasoningEngine
from src.application.architecture.drift_reasoning_engine import DriftReasoningEngine
from src.application.architecture.architecture_timeline_engine import ArchitectureTimelineEngine
from src.application.architecture.architecture_benchmark_engine import ArchitectureBenchmarkEngine
from src.application.architecture.architecture_similarity_engine import ArchitectureSimilarityEngine
from src.application.architecture.ownership_reasoning_engine import OwnershipReasoningEngine
from src.application.architecture.refactoring_reasoning_engine import RefactoringReasoningEngine
from src.application.architecture.architecture_recommendation_engine import ArchitectureRecommendationEngine
from src.application.architecture.bounded_context_engine import BoundedContextEngine
from src.application.architecture.architecture_artifact_service import ArchitectureArtifactService
from src.presentation.schemas.architecture_schemas import (
    ArchitectureProfileResponse,
    ArchitectureSnapshotResponse,
    ArchitectureFitnessResponse,
    ArchitectureViolationResponse,
    ArchitectureInvariantResponse,
    ArchitectureDriftResponse,
    ArchitectureTimelineResponse,
    ArchitectureBenchmarkResponse,
    ArchitectureSimilarityResponse,
    OwnershipProfileResponse,
    RefactoringCandidateResponse,
    ArchitectureRecommendationResponse,
    ArchitectureGraphResponse
)

router = APIRouter(prefix="/architecture", tags=["Architecture Intelligence"])

@router.post("/{repository_id}/profile", response_model=ArchitectureProfileResponse)
async def analyze_architecture_profile(
    repository_id: str,
    commit_hash: str = Query(...),
    architecture_reasoning_engine: ArchitectureReasoningEngine = Depends(get_architecture_reasoning_engine),
    architecture_artifact_service: ArchitectureArtifactService = Depends(get_architecture_artifact_service)
):
    """Detects the architecture profile for a given repository and commit."""
    try:
        profile = architecture_reasoning_engine.detect_architecture(repository_id, commit_hash)
        # Assuming persist_artifact takes the object and UoW handles the rest
        architecture_artifact_service.persist_profile(profile)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{repository_id}/snapshot", response_model=ArchitectureSnapshotResponse)
async def create_architecture_snapshot(
    repository_id: str,
    commit_hash: str = Query(...),
    architecture_artifact_service: ArchitectureArtifactService = Depends(get_architecture_artifact_service)
):
    """Generates and persists an architectural snapshot."""
    try:
        snapshot = architecture_artifact_service.create_snapshot(repository_id, commit_hash)
        return snapshot
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repository_id}/fitness", response_model=ArchitectureFitnessResponse)
async def compute_architecture_fitness(
    repository_id: str,
    commit_hash: str = Query(...),
    fitness_function_engine: FitnessFunctionEngine = Depends(get_fitness_function_engine)
):
    """Computes architectural fitness metrics."""
    try:
        fitness = fitness_function_engine.compute_fitness(repository_id, commit_hash)
        return fitness
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repository_id}/violations", response_model=List[ArchitectureViolationResponse])
async def detect_architecture_violations(
    repository_id: str,
    commit_hash: str = Query(...),
    invariant_reasoning_engine: InvariantReasoningEngine = Depends(get_invariant_reasoning_engine)
):
    """Detects architectural invariant violations."""
    try:
        violations = invariant_reasoning_engine.evaluate_invariants(repository_id, commit_hash)
        return violations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/invariants", response_model=List[ArchitectureInvariantResponse])
async def list_architecture_invariants(
    invariant_reasoning_engine: InvariantReasoningEngine = Depends(get_invariant_reasoning_engine)
):
    """Lists all defined architectural invariants."""
    try:
        invariants = invariant_reasoning_engine.get_all_invariants()
        return invariants
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repository_id}/drift", response_model=ArchitectureDriftResponse)
async def detect_architecture_drift(
    repository_id: str,
    from_commit: str = Query(...),
    to_commit: str = Query(...),
    drift_reasoning_engine: DriftReasoningEngine = Depends(get_drift_reasoning_engine)
):
    """Detects architectural drift between two commits."""
    try:
        drift = drift_reasoning_engine.detect_drift(repository_id, from_commit, to_commit)
        return drift
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repository_id}/timeline", response_model=ArchitectureTimelineResponse)
async def generate_architecture_timeline(
    repository_id: str,
    architecture_timeline_engine: ArchitectureTimelineEngine = Depends(get_architecture_timeline_engine)
):
    """Generates an evolution sequence of architectural state over time."""
    try:
        timeline = architecture_timeline_engine.generate_timeline(repository_id)
        return timeline
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repository_id}/benchmark", response_model=ArchitectureBenchmarkResponse)
async def benchmark_architecture(
    repository_id: str,
    commit_hash: str = Query(...),
    architecture_benchmark_engine: ArchitectureBenchmarkEngine = Depends(get_architecture_benchmark_engine)
):
    """Compares architecture fitness against peer repositories."""
    try:
        benchmark = architecture_benchmark_engine.compute_benchmark(repository_id, commit_hash)
        return benchmark
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repository_id}/similarity", response_model=ArchitectureSimilarityResponse)
async def compute_architecture_similarity(
    repository_id: str,
    target_repository_id: str = Query(...),
    architecture_similarity_engine: ArchitectureSimilarityEngine = Depends(get_architecture_similarity_engine)
):
    """Computes similarity between two repositories."""
    try:
        similarity = architecture_similarity_engine.compute_similarity(repository_id, target_repository_id)
        return similarity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repository_id}/ownership", response_model=OwnershipProfileResponse)
async def detect_ownership_profile(
    repository_id: str,
    commit_hash: str = Query(...),
    ownership_reasoning_engine: OwnershipReasoningEngine = Depends(get_ownership_reasoning_engine)
):
    """Analyzes ownership and highlights silos and bus factors."""
    try:
        profile = ownership_reasoning_engine.detect_ownership(repository_id, commit_hash)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repository_id}/refactoring", response_model=List[RefactoringCandidateResponse])
async def detect_refactoring_candidates(
    repository_id: str,
    commit_hash: str = Query(...),
    refactoring_reasoning_engine: RefactoringReasoningEngine = Depends(get_refactoring_reasoning_engine)
):
    """Detects structural code smells and refactoring candidates."""
    try:
        candidates = refactoring_reasoning_engine.detect_candidates(repository_id, commit_hash)
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repository_id}/recommendations", response_model=List[ArchitectureRecommendationResponse])
async def generate_architecture_recommendations(
    repository_id: str,
    commit_hash: str = Query(...),
    architecture_recommendation_engine: ArchitectureRecommendationEngine = Depends(get_architecture_recommendation_engine)
):
    """Generates actionable structural recommendations."""
    try:
        recommendations = architecture_recommendation_engine.generate_recommendations(repository_id, commit_hash)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repository_id}/bounded-contexts")
async def detect_bounded_contexts(
    repository_id: str,
    commit_hash: str = Query(...),
    bounded_context_engine: BoundedContextEngine = Depends(get_bounded_context_engine)
):
    """Identifies bounded contexts."""
    try:
        contexts = bounded_context_engine.detect_contexts(repository_id, commit_hash)
        # Simplified return type since we don't have a specific schema
        return {"contexts": contexts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

