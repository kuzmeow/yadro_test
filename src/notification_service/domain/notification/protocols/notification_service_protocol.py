from typing import Protocol

from notification_service.domain.notification.entities.notification_entity import Notification


class NotificationServiceProtocol(Protocol):
    async def send_notification(self, notification: Notification) -> None:
        """Отправить уведомление.

        :param notification: Доменная сущность уведомления.
        :return: None
        """
