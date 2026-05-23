"""Задачи TaskIQ, связанные с отправкой уведомлений."""

from dishka import FromDishka
from dishka.integrations.taskiq import inject

from notification_service.application.services.notification_service import NotificationService
from notification_service.domain.common.protocols.logger_factory_protocol import LoggerFactory
from notification_service.domain.notification.entities.notification_entity import Notification
from notification_service.domain.notification.exceptions.notification_exceptions import NotificationSendingFailed
from notification_service.domain.notification.protocols.notification_db_repo_protocol import NotificationDBProtocol
from notification_service.infra.taskiq.taskiq_broker import broker


@broker.task
@inject(patch_module=True)
async def send_notification(
    notification: Notification,
    notification_db_repo: FromDishka[NotificationDBProtocol],
    notification_service: FromDishka[NotificationService],
    logger_factory: FromDishka[LoggerFactory],
) -> None:
    """Отправить уведомление.

    :param notification: Доменная сущность уведомления.
    :param notification_db_repo: Репозиторий уведомлений (инжектится через Dishka).
    :param notification_service: Сервис отправки уведомлений (инжектится через Dishka).
    :param logger_factory: Фабрика логгера (инжектится через Dishka).
    :return: None
    """
    logger = logger_factory(__name__)
    logger.info(f"Starting notification {notification.uid} sending process..")

    notification.set_pending()
    await notification_db_repo.update_status(entity=notification)

    try:
        await notification_service.send_notification(notification=notification)
    except Exception as exc:
        if isinstance(exc, NotificationSendingFailed):
            logger.error("Notification Sending Failed", extra={"details": exc.details})
            notification.error_text = str(exc.details)
        else:
            logger.exception(
                f"Unhandled {type(exc).__name__} while sending notification", extra={"error_class": type(exc).__name__}
            )
            notification.error_text = "Internal Server Error"
        notification.set_failed()
        await notification_db_repo.update_status(entity=notification)
        return

    notification.set_sent()
    await notification_db_repo.update_status(entity=notification)
    logger.info(f"Finished notification {notification.uid} sending process")
