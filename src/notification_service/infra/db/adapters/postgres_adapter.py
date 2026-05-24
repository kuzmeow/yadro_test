"""Адаптер для подключения к PostgreSQL через SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from notification_service.application.config import ApplicationSettings


class PostgresAdapter:
    """Синхронный адаптер для PostgreSQL."""

    def __init__(self, settings: ApplicationSettings) -> None:
        db_url = settings.DATABASE_URL
        self._engine = create_engine(
            url=db_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        self._session_factory = sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autocommit=False,
        )

    @property
    def get_session(self) -> sessionmaker[Session]:
        """Фабрика синхронных сессий."""
        return self._session_factory
