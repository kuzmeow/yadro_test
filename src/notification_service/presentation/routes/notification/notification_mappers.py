from notification_service.domain.notification.entities.dto.notification_dto import (
    EnqueueNotificationDTO,
    SearchNotificationDTO,
)
from notification_service.domain.notification.entities.notification_entity import Notification
from notification_service.presentation.routes.notification.notification_schemas import (
    EnqueueNotificationSchema,
    ReadNotificationSchema,
    SearchNotificationSchema,
)


def to_enqueue_notification_dto(schema: EnqueueNotificationSchema) -> EnqueueNotificationDTO:
    channel_data_dict = schema.channel_data.model_dump() if schema.channel_data is not None else None
    return EnqueueNotificationDTO(
        type=schema.type,
        recipient=schema.recipient,
        subject=schema.subject,
        message=schema.message,
        channel_data=channel_data_dict,
    )


def to_search_notification_dto(schema: SearchNotificationSchema) -> SearchNotificationDTO:
    return SearchNotificationDTO(
        status=schema.status,
        limit=schema.limit,
        offset=schema.offset,
    )


def to_read_notification_schema(entity: Notification) -> ReadNotificationSchema:
    return ReadNotificationSchema(
        uid=entity.uid,
        status=entity.status,
        error=entity.error_text,
    )
