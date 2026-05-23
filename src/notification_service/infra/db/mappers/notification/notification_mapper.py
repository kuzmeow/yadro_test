from notification_service.domain.notification.entities.notification_entity import Notification as NotificationEntity
from notification_service.infra.db.models import Notification as NotificationModel


class NotificationMapper:
    """Маппер между различными представлениями сущности."""

    @staticmethod
    def orm_to_entity(obj: NotificationModel) -> NotificationEntity:
        """Преобразовать модель ORM в доменную сущность."""

        return NotificationEntity.reconstitute(
            uid=obj.uid,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            notification_type=obj.type,
            recipient=obj.recipient,
            subject=obj.subject,
            message=obj.message,
            channel_data=obj.channel_data,
            status=obj.status,
        )
