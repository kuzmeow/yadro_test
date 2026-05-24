from dishka import Provider, Scope, provide
from sqlalchemy.orm import Session

from notification_service.application.services.notification_service import NotificationService
from notification_service.application.use_cases.notification.enqueue_notification_use_case import (
    EnqueueNotificationUseCase,
)
from notification_service.domain.common.entities.value_objects.config import PaginationConfig
from notification_service.domain.common.protocols.logger_factory_protocol import LoggerFactory
from notification_service.domain.notification.protocols.notification_db_repo_protocol import NotificationDBProtocol
from notification_service.domain.notification.protocols.notification_service_protocol import NotificationServiceProtocol
from notification_service.domain.notification.protocols.notification_tasks_protocol import NotificationTasksProtocol
from notification_service.infra.db.mappers.notification.notification_mapper import NotificationMapper
from notification_service.infra.db.repositories.notification.notification_db_repository import NotificationPgRepository
from notification_service.infra.taskiq.adapters.taskiq_user_adapter import TaskIQNotificationTasksAdapter
from notification_service.infra.taskiq.post_commit_queue import PostCommitQueue


class NotificationProvider(Provider):
    """Провайдер зависимостей для уведомлений."""

    scope = Scope.REQUEST

    @provide
    def get_project_db_repo(
        self, db: Session, mapper: NotificationMapper, pagination_config: PaginationConfig
    ) -> NotificationDBProtocol:
        return NotificationPgRepository(db=db, mapper=mapper, pagination_config=pagination_config)

    @provide
    def get_notification_tasks(self, post_commit_queue: PostCommitQueue) -> NotificationTasksProtocol:
        return TaskIQNotificationTasksAdapter(queue=post_commit_queue)

    @provide
    def get_notification_service(self, logger_factory: LoggerFactory) -> NotificationServiceProtocol:
        return NotificationService(logger_factory=logger_factory)

    @provide
    def get_enqueue_notification_use_case(
        self,
        notification_db_repo: NotificationDBProtocol,
        notification_tasks: NotificationTasksProtocol,
        logger_factory: LoggerFactory,
    ) -> EnqueueNotificationUseCase:
        return EnqueueNotificationUseCase(
            notification_db_repo=notification_db_repo,
            notification_tasks=notification_tasks,
            logger_factory=logger_factory,
        )
