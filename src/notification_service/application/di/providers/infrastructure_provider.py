from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.application.config import ApplicationSettings
from notification_service.domain.common.entities.value_objects.config import LoggerConfig
from notification_service.domain.common.protocols.logger_factory_protocol import LoggerFactory
from notification_service.infra.broker.adapters.redis_adapter import RedisAdapter
from notification_service.infra.db.adapters.postgres_adapter import PostgresAdapter
from notification_service.infra.db.mappers.notification.notification_mapper import NotificationMapper
from notification_service.infra.logger.project_logger import ProjectLogger


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
    async def get_db_session(self, adapter: PostgresAdapter) -> AsyncGenerator[AsyncSession]:
        """Получить сессию SQLAlchemy из адаптера."""
        async with adapter.get_session() as session:
            exc = yield session
            if exc is not None:
                await session.rollback()
            else:
                await session.commit()

    @provide(scope=Scope.REQUEST)
    async def get_broker_client(self, adapter: RedisAdapter) -> AsyncGenerator[Redis]:
        """Получить клиента Redis из адаптера."""
        async with adapter.get_client() as client:
            yield client

    @provide
    def get_project_logger(self, settings: LoggerConfig) -> ProjectLogger:
        return ProjectLogger(settings=settings)

    @provide(scope=Scope.APP)
    def get_logger_factory(self, project_logger: ProjectLogger) -> LoggerFactory:
        return project_logger.get_logger

    @provide(scope=Scope.APP)
    def get_project_mapper(self) -> NotificationMapper:
        return NotificationMapper()
