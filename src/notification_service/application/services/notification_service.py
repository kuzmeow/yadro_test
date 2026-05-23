from random import random

from asgiref.server import logger

from notification_service import LoggerFactory
from notification_service.domain.notification.entities.notification_entity import Notification
from notification_service.domain.notification.exceptions.notification_exceptions import NotificationSendingFailed
from notification_service.domain.notification.protocols.notification_service_protocol import NotificationServiceProtocol


class NotificationService(NotificationServiceProtocol):
    def __init__(self, logger_factory: LoggerFactory) -> None:
        self.logger = logger_factory(__name__)

    async def send_notification(self, notification: Notification) -> None:
        """Отправить уведомление.

        :param notification: Доменная сущность уведомления.
        :raises: NotificationSendingFailed: Ошибка при отправке уведомления
        :return: None
        """
        self.logger.info(f"Sending notification {notification.uid}")

        # симуляция работы сервиса по отправке уведомлений
        if random() > 0.8:
            logger.error(f"Simulated error occurred while sending notification {notification.uid}")
            message = "Simulated error"
            raise NotificationSendingFailed(details={"message": message})

        self.logger.info(f"Notification {notification.uid} sent successfully")
