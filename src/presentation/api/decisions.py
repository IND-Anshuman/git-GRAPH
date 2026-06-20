from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID

from src.presentation.schemas.decision_schemas import DecisionSchema, DecisionCreate
from src.presentation.dependencies import get_uow

router = APIRouter(prefix="/decisions", tags=["decisions"])

@router.get("/{repository_id}", response_model=List[DecisionSchema])
def list_decisions(repository_id: str, uow=Depends(get_uow)):
    with uow:
        # returns simple mock for now
        return []

@router.get("/decision/{decision_id}", response_model=DecisionSchema)
def get_decision(decision_id: UUID, uow=Depends(get_uow)):
    with uow:
        decision = uow.decisions.get_by_id(str(decision_id))
        if not decision:
            raise HTTPException(status_code=404, detail="Decision not found")
        return decision
        
@router.get("/decision/{decision_id}/conflicts")
def get_decision_conflicts(decision_id: UUID, uow=Depends(get_uow)):
    return []
    
@router.get("/decision/{decision_id}/fitness")
def get_decision_fitness(decision_id: UUID, uow=Depends(get_uow)):
    return {"fitness": 0.8}
