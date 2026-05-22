"""Адаптер для подключения к PostgreSQL через SQLAlchemy."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from notification_service.application.config import ApplicationSettings


class PostgresAdapter:
    """Управляет созданием движка и фабрики асинхронных сессий."""

    def __init__(self, settings: ApplicationSettings) -> None:
        """Создать движок на основе URL из конфигурации."""

        self._engine = create_async_engine(url=settings.DATABASE_URL)
        self._session_factory = async_sessionmaker(bind=self._engine, expire_on_commit=False, autocommit=False)

    @property
    def get_session(self) -> async_sessionmaker[AsyncSession]:
        """Предоставить фабрику асинхронных сессий SQLAlchemy.

        :return: Фабрика `async_sessionmaker`.
        """
        return self._session_factory
