"""Engine to compute the overall temporal graph health score based on multiple validation scores."""

import logging
from typing import Dict, Any

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId
from src.application.services.seid_validation_engine import SEIDValidationEngine

logger = logging.getLogger(__name__)

class HealthScoreEngine:
    """Calculates repository temporal graph health score using weighted parameters."""

    def __init__(self, seid_engine: SEIDValidationEngine) -> None:
        self.seid_engine = seid_engine

    def calculate_health_score(self, uow: IUnitOfWork, repository_id: RepositoryId) -> Dict[str, Any]:
        """Calculates system-wide health score metrics for a given repository."""
        
        # 1. Retrieve all entities for count denominator
        entities = uow.code_entities.get_by_repository(repository_id)
        entity_count = len(entities)

        # 2. Reconstruction Score (s_rec)
        # Fetch the latest accuracy report
        accuracy_reports = uow.metrics.list_accuracy_reports(repository_id)
        if accuracy_reports:
            s_rec = accuracy_reports[0].reconstruction_accuracy
        else:
            s_rec = 1.0 # default to 1.0 if no checks have run

        # 3. Integrity Score (s_int)
        violations = uow.integrity.list_violations_by_repository(repository_id, unresolved_only=True)
        violation_count = len(violations)
        s_int = 1.0 - min(1.0, violation_count / max(1, entity_count))

        # 4. Confidence Score (s_conf)
        events = uow.change_events.list_by_repository(repository_id)
        if events:
            total_conf = sum(ce.confidence for ce in events)
            s_conf = total_conf / len(events)
        else:
            s_conf = 1.0

        # 5. SEID Score (s_seid)
        seid_result = self.seid_engine.validate_seid_stability(uow, repository_id)
        if seid_result["status"] == "PASSED":
            s_seid = 1.0
        else:
            errors_count = len(seid_result["errors"])
            s_seid = 1.0 - min(1.0, errors_count / max(1, entity_count))

        # 6. Weighted Sum & Normalization
        # Weights: 40% rec, 30% int, 15% conf, 15% seid
        health_score = (0.40 * s_rec + 0.30 * s_int + 0.15 * s_conf + 0.15 * s_seid) * 100.0

        # Categorize status
        if health_score >= 90.0:
            status = "Healthy"
        elif health_score >= 70.0:
            status = "Degraded"
        else:
            status = "Corrupt"

        return {
            "health_score": round(health_score, 1),
            "reconstruction_score": round(s_rec * 100, 1),
            "integrity_score": round(s_int * 100, 1),
            "confidence_score": round(s_conf * 100, 1),
            "seid_stability_score": round(s_seid * 100, 1),
            "status": status
        }
