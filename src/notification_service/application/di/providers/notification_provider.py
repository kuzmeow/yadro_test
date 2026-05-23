from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.domain.common.entities.value_objects.config import PaginationConfig
from notification_service.domain.notification.protocols.notification_db_repo_protocol import NotificationDBProtocol
from notification_service.infra.db.mappers.notification.notification_mapper import NotificationMapper
from notification_service.infra.db.repositories.notification.notification_db_repository import NotificationPgRepository


class ProjectProvider(Provider):
    """Провайдер зависимостей для уведомлений."""

    scope = Scope.REQUEST

    @provide
    def get_project_db_repo(
        self, db: AsyncSession, mapper: NotificationMapper, pagination_config: PaginationConfig
    ) -> NotificationDBProtocol:
        return NotificationPgRepository(db=db, mapper=mapper, pagination_config=pagination_config)
