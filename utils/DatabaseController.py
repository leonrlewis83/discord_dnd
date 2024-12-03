from typing import Optional, Dict, List
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

# Base for all ORM models
Base = declarative_base()

class DatabaseController:
    def __init__(self, db_host: str, db_port: int, db_user: str, db_password: str, db_name: str, dialect: str = "postgresql", driver: Optional[str] = None):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.dialect = dialect
        self.driver = driver

        self.db_url = self._construct_db_url()
        self.engine = create_engine(self.db_url, pool_size=5, max_overflow=10)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        Base.metadata.create_all(bind=self.engine)

    def _construct_db_url(self) -> str:
        driver_part = f"+{self.driver}" if self.driver else ""
        return f"{self.dialect}{driver_part}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @contextmanager
    def session_scope(self) -> Session:
        """Provide a transactional scope for a series of operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise
        finally:
            session.close()

    def fetch_all(self, model: Base, filters: Optional[Dict] = None) -> List[Base]:
        """Fetch all rows matching optional filters."""
        with self.session_scope() as session:
            query = session.query(model)
            if filters:
                query = query.filter_by(**filters)
            return query.all()

    def fetch_one(self, model: Base, filters: Optional[Dict] = None) -> Optional[Base]:
        """Fetch a single row matching optional filters."""
        with self.session_scope() as session:
            query = session.query(model)
            if filters:
                query = query.filter_by(**filters)
            return query.first()

    def fetch_count(self, model: Base, filters: Optional[Dict] = None) -> int:
        """Fetch the count of rows matching optional filters."""
        with self.session_scope() as session:
            query = session.query(model)
            if filters:
                query = query.filter_by(**filters)
            return query.count()

    def insert(self, obj: Base) -> None:
        """Insert a single ORM object."""
        with self.session_scope() as session:
            session.add(obj)

    def update(self, model: Base, filters: Dict, updates: Dict) -> None:
        """Update rows in a table."""
        with self.session_scope() as session:
            session.query(model).filter_by(**filters).update(updates)

    def delete(self, model: Base, filters: Dict) -> None:
        """Delete rows in a table."""
        with self.session_scope() as session:
            session.query(model).filter_by(**filters).delete()
