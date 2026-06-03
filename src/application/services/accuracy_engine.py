"""Accuracy evaluation engine for comparing temporal changes against ground truth datasets."""

import datetime
import json
import logging
import uuid
from typing import Dict, Any, Set, Tuple

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.entities.metrics import AccuracyReport
from src.application.services.reconstruction_validation_engine import ReconstructionValidationEngine

logger = logging.getLogger(__name__)

class AccuracyEngine:
    """Calculates precision, recall, and event alignment against ground-truth timelines."""

    def __init__(self, validation_engine: ReconstructionValidationEngine) -> None:
        self.validation_engine = validation_engine

    def evaluate_accuracy(
        self,
        uow: IUnitOfWork,
        repository_id: RepositoryId,
        ground_truth_data: Dict[str, Any],
        target_commit_hash: str
    ) -> AccuracyReport:
        """Evaluates prediction precision and recall, then logs an AccuracyReport."""
        
        # 1. Parse predicted change events from DB
        predicted_set: Set[Tuple[str, str, str]] = set()
        rename_predicted: Set[Tuple[str, str]] = set()
        move_predicted: Set[Tuple[str, str]] = set()

        db_events = uow.change_events.list_by_repository(repository_id)
        for ce in db_events:
            ev = uow.entity_versions.get_latest_before_or_at(ce.seid, ce.commit_hash)
            if not ev:
                continue
            
            event_type_str = ce.change_type.name
            pred_tuple = (ce.commit_hash, ev.canonical_name, event_type_str)
            predicted_set.add(pred_tuple)

            if event_type_str == "RENAMED":
                rename_predicted.add((ce.commit_hash, ev.canonical_name))
            elif event_type_str == "MOVED":
                move_predicted.add((ce.commit_hash, ev.canonical_name))

        # 2. Parse expected change events from ground truth
        expected_set: Set[Tuple[str, str, str]] = set()
        rename_expected: Set[Tuple[str, str]] = set()
        move_expected: Set[Tuple[str, str]] = set()

        expected_timeline = ground_truth_data.get("expected_timeline", [])
        for item in expected_timeline:
            commit_hash = item["commit_hash"]
            for change in item["changes"]:
                canonical_name = change["canonical_name"]
                change_type_str = change["change_type"]
                expected_set.add((commit_hash, canonical_name, change_type_str))

                if change_type_str == "RENAMED":
                    rename_expected.add((commit_hash, canonical_name))
                elif change_type_str == "MOVED":
                    move_expected.add((commit_hash, canonical_name))

        # 3. Calculate metrics
        # Rename Precision and Recall
        rename_matches = rename_predicted.intersection(rename_expected)
        rename_precision = len(rename_matches) / len(rename_predicted) if rename_predicted else 1.0
        rename_recall = len(rename_matches) / len(rename_expected) if rename_expected else 1.0

        # Move Precision and Recall
        move_matches = move_predicted.intersection(move_expected)
        move_precision = len(move_matches) / len(move_predicted) if move_predicted else 1.0
        move_recall = len(move_matches) / len(move_expected) if move_expected else 1.0

        # Overall Event Accuracy
        event_matches = predicted_set.intersection(expected_set)
        event_accuracy = len(event_matches) / len(expected_set) if expected_set else 1.0

        # 4. Measure reconstruction accuracy
        recon_report = self.validation_engine.verify_reconstruction_accuracy(
            uow, repository_id, target_commit_hash
        )

        # 5. Build and save report
        report = AccuracyReport(
            id=uuid.uuid4(),
            repository_id=repository_id,
            commit_hash=target_commit_hash,
            rename_precision=rename_precision,
            rename_recall=rename_recall,
            move_precision=move_precision,
            move_recall=move_recall,
            event_accuracy=event_accuracy,
            reconstruction_accuracy=recon_report.reconstruction_accuracy,
            measured_at=datetime.datetime.now(datetime.timezone.utc)
        )

        uow.metrics.save_accuracy_report(report)
        return report
