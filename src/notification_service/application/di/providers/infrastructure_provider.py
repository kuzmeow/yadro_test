from collections.abc import Generator

from dishka import Provider, Scope, provide
from redis import Redis
from sqlalchemy.orm import Session

from notification_service.application.config import ApplicationSettings
from notification_service.domain.common.entities.value_objects.config import LoggerConfig
from notification_service.domain.common.protocols.logger_factory_protocol import LoggerFactory
from notification_service.infra.broker.adapters.redis_adapter import RedisAdapter
from notification_service.infra.db.adapters.postgres_adapter import PostgresAdapter
from notification_service.infra.db.mappers.notification.notification_mapper import NotificationMapper
from notification_service.infra.logger.project_logger import ProjectLogger
from notification_service.infra.taskiq.background_loop_manager import BackgroundLoopManager
from notification_service.infra.taskiq.post_commit_queue import PostCommitQueue


class InfraProvider(Provider):
    """Провайдер инфраструктурных зависимостей."""

    scope = Scope.APP

    @provide
    def get_loop_manager(self, logger_factory: LoggerFactory) -> BackgroundLoopManager:
        manager = BackgroundLoopManager(logger_factory=logger_factory)
        manager.start()
        return manager

    @provide
    def get_db_adapter(self, settings: ApplicationSettings) -> PostgresAdapter:
        return PostgresAdapter(settings=settings)

    @provide
    def get_redis_adapter(self, settings: ApplicationSettings) -> RedisAdapter:
        return RedisAdapter(settings=settings)

    @provide(scope=Scope.REQUEST)
    def get_db_session(self, adapter: PostgresAdapter, post_commit_queue: PostCommitQueue) -> Generator[Session]:
        """Синхронный генератор сессии. Коммит/роллбэк/закрытие."""
        session = adapter.get_session()
        try:
            yield session
            session.commit()
            post_commit_queue.execute_all()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @provide(scope=Scope.REQUEST)
    def get_broker_client(self, adapter: RedisAdapter) -> Generator[Redis]:
        """Синхронный генератор для Redis-клиента."""
        client = adapter.get_client()
        yield client

    @provide(scope=Scope.REQUEST)
    def get_post_commit_queue(
        self, logger_factory: LoggerFactory, loop_manager: BackgroundLoopManager
    ) -> PostCommitQueue:
        return PostCommitQueue(logger_factory=logger_factory, loop_manager=loop_manager)

    @provide
    def get_project_logger(self, settings: LoggerConfig) -> ProjectLogger:
        return ProjectLogger(settings=settings)

    @provide(scope=Scope.APP)
    def get_logger_factory(self, project_logger: ProjectLogger) -> LoggerFactory:
        return project_logger.get_logger

    @provide(scope=Scope.APP)
    def get_project_mapper(self) -> NotificationMapper:
        return NotificationMapper()
