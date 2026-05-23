import asyncio
from collections.abc import Generator

from dishka import Provider, Scope, provide
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.application.config import ApplicationSettings
from notification_service.domain.common.entities.value_objects.config import LoggerConfig
from notification_service.domain.common.protocols.logger_factory_protocol import LoggerFactory
from notification_service.infra.broker.adapters.redis_adapter import RedisAdapter
from notification_service.infra.db.adapters.postgres_adapter import PostgresAdapter
from notification_service.infra.db.mappers.notification.notification_mapper import NotificationMapper
from notification_service.infra.logger.project_logger import ProjectLogger


def _run_async(coro):
    """Безопасный запуск async-кода из sync-контекста. Работает в uvicorn, pytest, CLI."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    return loop.run_until_complete(coro)


class InfraProvider(Provider):
    """Провайдер инфраструктурных зависимостей."""

    scope = Scope.APP

    @provide
    def get_db_adapter(self, settings: ApplicationSettings) -> PostgresAdapter:
        """Создать адаптер PostgreSQL."""
        return PostgresAdapter(settings=settings)

    @provide
    def get_redis_adapter(self, settings: ApplicationSettings) -> RedisAdapter:
        """Создать адаптер Redis."""
        return RedisAdapter(settings=settings)

    @provide(scope=Scope.REQUEST)
    def get_db_session(self, adapter: PostgresAdapter) -> Generator[AsyncSession]:
        """Sync-генератор сессии."""
        session = adapter.get_session()

        try:
            yield session
        except Exception:
            _run_async(session.rollback())
            raise
        else:
            try:
                _run_async(session.commit())
            except Exception:
                _run_async(session.rollback())
                raise
        finally:
            _run_async(session.close())

    @provide(scope=Scope.REQUEST)
    def get_broker_client(self, adapter: RedisAdapter) -> Generator[Redis]:
        """Sync-генератор Redis-клиента."""
        cm = adapter.get_client()
        client = _run_async(cm.__aenter__())
        try:
            yield client
        finally:
            _run_async(cm.__aexit__(None, None, None))

    @provide
    def get_project_logger(self, settings: LoggerConfig) -> ProjectLogger:
        return ProjectLogger(settings=settings)

    @provide(scope=Scope.APP)
    def get_logger_factory(self, project_logger: ProjectLogger) -> LoggerFactory:
        return project_logger.get_logger

    @provide(scope=Scope.APP)
    def get_project_mapper(self) -> NotificationMapper:
        return NotificationMapper()
