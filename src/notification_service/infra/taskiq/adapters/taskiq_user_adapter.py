from notification_service.domain.notification.entities.notification_entity import Notification
from notification_service.domain.notification.protocols.notification_tasks_protocol import NotificationTasksProtocol
from notification_service.infra.taskiq.tasks.notification_tasks import send_notification


class TaskIQNotificationTasksAdapter(NotificationTasksProtocol):
    @staticmethod
    async def enqueue_notification(notification: Notification) -> None:
        """Запланировать отправку уведомления.

        :param notification: Доменная сущность уведомления.
        :return: None
        """

        await send_notification.kiq(notification=notification)
