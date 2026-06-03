"""SQLAlchemy implementation of IMetricsRepository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domain.entities.metrics import AccuracyReport, BenchmarkReport
from src.domain.repositories.metrics_repo import IMetricsRepository
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.persistence.models.metrics_model import BenchmarkReportModel, AccuracyReportModel
from src.infrastructure.persistence.mappers.domain_mapper import DomainMapper

class SAMetricsRepository(IMetricsRepository):
    """SQLAlchemy repository for metrics (benchmarks and accuracy)."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save_accuracy_report(self, report: AccuracyReport) -> None:
        model = DomainMapper.to_accuracy_report_model(report)
        self.session.merge(model)

    def get_accuracy_report_by_commit(self, repo_id: RepositoryId, commit_hash: str) -> Optional[AccuracyReport]:
        stmt = select(AccuracyReportModel).where(
            AccuracyReportModel.repository_id == repo_id.value,
            AccuracyReportModel.commit_hash == commit_hash
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        if model:
            return DomainMapper.to_accuracy_report_entity(model)
        return None

    def list_accuracy_reports(self, repo_id: RepositoryId) -> List[AccuracyReport]:
        stmt = select(AccuracyReportModel).where(
            AccuracyReportModel.repository_id == repo_id.value
        ).order_by(AccuracyReportModel.measured_at.desc())
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_accuracy_report_entity(m) for m in models]

    def save_benchmark_report(self, report: BenchmarkReport) -> None:
        model = DomainMapper.to_benchmark_report_model(report)
        self.session.merge(model)

    def list_benchmark_reports(self, repo_id: RepositoryId) -> List[BenchmarkReport]:
        stmt = select(BenchmarkReportModel).where(
            BenchmarkReportModel.repository_id == repo_id.value
        ).order_by(BenchmarkReportModel.measured_at.desc())
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_benchmark_report_entity(m) for m in models]
