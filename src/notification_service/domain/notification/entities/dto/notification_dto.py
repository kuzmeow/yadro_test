from dataclasses import dataclass
from typing import Any

from notification_service.domain.notification.entities.enums.notification_enums import (
    NotificationStatusEnum,
    NotificationTypeEnum,
)


@dataclass(frozen=True)
class NotificationRegistrationDTO:
    type: NotificationTypeEnum
    recipient: str
    subject: str | None
    message: str
    channel_data: dict[str, Any] | None


@dataclass(frozen=True)
class NotificationSearchDTO:
    status: NotificationStatusEnum | None
    limit: int | None
    offset: int | None
