from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class DecisionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    description: str
    decision_type: str
    status: str
    confidence_score: float
    first_seen_commit: str
    last_seen_commit: str
    repository_id: str
    created_at: datetime

class DecisionCreate(BaseModel):
    name: str
    description: str
    decision_type: str
    status: str
    repository_id: str
