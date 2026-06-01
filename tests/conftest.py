import pytest
from unittest.mock import Mock

@pytest.fixture
def db_engine():
    from sqlalchemy import create_engine
    return create_engine("sqlite:///:memory:")

@pytest.fixture
def db_session(db_engine):
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_repository_entity():
    class RepoMock:
        id = "repo-id"
        url = "https://github.com/test/repo"
        status = "PENDING"
    return RepoMock()

@pytest.fixture
def sample_source_file():
    class SourceFileMock:
        id = "file-id"
        path = "src/main.py"
        language = "PYTHON"
    return SourceFileMock()

@pytest.fixture
def identity_service():
    class IdentityServiceMock:
        def compute_seid(self, *args, **kwargs):
            return "test-seid-1234"
        def compute_content_hash(self, *args, **kwargs):
            return "hash-1234"
        def compute_qualified_name(self, components):
            return ".".join(components)
    return IdentityServiceMock()
