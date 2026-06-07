import os
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from src.application.use_cases.delete_repository import DeleteRepositoryUseCase
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.entities.repository import RepositoryEntity
from src.domain.enums.analysis_status import AnalysisStatus
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork

class DummyEngine:
    def __init__(self, session):
        self.session_factory = lambda: session


def test_delete_repository_success(db_session):
    uow_factory = lambda: SQLAlchemyUnitOfWork(DummyEngine(db_session))
    
    # 1. Create and save a dummy repository entity
    repo_id = RepositoryId.generate()
    repo_path = "/tmp/fake_clone_path"
    
    repo = RepositoryEntity(
        id=repo_id,
        url="https://github.com/user/repo-to-delete",
        name="delete-repo",
        default_branch="main",
        local_path=repo_path,
        status=AnalysisStatus.COMPLETED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    with uow_factory() as uow:
        uow.repositories.save(repo)
        uow.commit()

    use_case = DeleteRepositoryUseCase(uow_factory=uow_factory)
    
    # 2. Patch os.path.exists and shutil.rmtree to simulate folder cleanup
    with patch("os.path.exists") as mock_exists, patch("shutil.rmtree") as mock_rmtree:
        mock_exists.return_value = True
        
        success = use_case.execute(str(repo_id.value))
        
        assert success is True
        mock_exists.assert_called_once_with(repo_path)
        mock_rmtree.assert_called_once()

    # 3. Verify repository is deleted from database
    with uow_factory() as uow:
        deleted_repo = uow.repositories.get_by_id(repo_id)
        assert deleted_repo is None
