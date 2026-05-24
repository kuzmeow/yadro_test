"""Протокол фоновых задач, связанных с рассылкой уведомлений."""

from typing import Protocol

from notification_service.domain.notification.entities.notification_entity import Notification


class NotificationTasksProtocol(Protocol):
    """Контракт адаптера постановки задач на отправку уведомлений."""

    def enqueue_notification(self, notification: Notification) -> None:
        """Запланировать отправку уведомления.

        :param notification: Доменная сущность уведомления.
        :return: None
        """
