from typing import Generic, TypeVar, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

T = TypeVar("T")

class SQLAlchemyRepository(Generic[T]):
    """Base generic repository for SQLAlchemy models."""

    def __init__(self, session: Session, model_class: type):
        self.session = session
        self.model_class = model_class

    def get_by_id(self, id: UUID) -> Optional[T]:
        return self.session.get(self.model_class, id)

    def add(self, entity: T) -> None:
        self.session.add(entity)

    def add_all(self, entities: List[T]) -> None:
        self.session.add_all(entities)

    def delete(self, entity: T) -> None:
        self.session.delete(entity)
