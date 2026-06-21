"""Database connection and session management."""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

class DatabaseEngine:
    """Manages the SQLAlchemy engine and session factory."""
    
    def __init__(self, database_url: str) -> None:
        """Initialize the database engine.
        
        Args:
            database_url: The SQLAlchemy connection string.
        """
        self.engine = create_engine(database_url)
        
        from sqlalchemy import event
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            import sqlite3
            if isinstance(dbapi_connection, sqlite3.Connection):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON;")
                cursor.close()

        self.session_factory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations.
        
        Yields:
            SQLAlchemy session object.
        """
        session: Session = self.session_factory()
        try:
            yield session
        finally:
            session.close()
