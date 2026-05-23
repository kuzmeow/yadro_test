from notification_service import LoggerFactory
from notification_service.domain.notification.entities.dto.notification_dto import EnqueueNotificationDTO
from notification_service.domain.notification.entities.notification_entity import Notification
from notification_service.domain.notification.protocols.notification_db_repo_protocol import NotificationDBProtocol
from notification_service.domain.notification.protocols.notification_tasks_protocol import NotificationTasksProtocol


class EnqueueNotificationUseCase:
    def __init__(
        self,
        notification_db_repo: NotificationDBProtocol,
        notification_tasks: NotificationTasksProtocol,
        logger_factory: LoggerFactory,
    ) -> None:
        self.notification_db_repo = notification_db_repo
        self.notification_tasks = notification_tasks
        self.logger = logger_factory(__name__)

    async def execute(self, dto: EnqueueNotificationDTO) -> Notification:
        """Добавить уведомление в очередь.

        :param dto: Данные добавления уведомления в очередь.
        :return: Доменная сущность добавленного уведомления.
        """
        notification = Notification.create(
            notification_type=dto.type,
            recipient=dto.recipient,
            subject=dto.subject,
            message=dto.message,
            channel_data=dto.channel_data,
        )
        self.logger.info(f"Enqueueing notification {notification.uid}")

        enqueued = await self.notification_db_repo.save(entity=notification)

        await self.notification_tasks.enqueue_notification(notification=notification)

        self.logger.info(f"Notification {notification.uid} enqueued")

        return enqueued
