from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

from src.domain.entities.metrics import AccuracyReport, BenchmarkReport
from src.domain.value_objects.repository_id import RepositoryId

class IMetricsRepository(ABC):
    """Abstract port for metrics repositories."""

    @abstractmethod
    def save_accuracy_report(self, report: AccuracyReport) -> None:
        """Save a validation accuracy report."""
        pass

    @abstractmethod
    def get_accuracy_report_by_commit(self, repo_id: RepositoryId, commit_hash: str) -> Optional[AccuracyReport]:
        """Fetch accuracy statistics of a specific commit analysis."""
        pass

    @abstractmethod
    def list_accuracy_reports(self, repo_id: RepositoryId) -> List[AccuracyReport]:
        """Fetch all accuracy logs of a repository."""
        pass

    @abstractmethod
    def save_benchmark_report(self, report: BenchmarkReport) -> None:
        """Save a performance benchmark report."""
        pass

    @abstractmethod
    def list_benchmark_reports(self, repo_id: RepositoryId) -> List[BenchmarkReport]:
        """Fetch all performance benchmark logs of a repository."""
        pass
