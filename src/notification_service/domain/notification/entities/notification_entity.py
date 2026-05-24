"""Сущность уведомления, используемая в доменном слое."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from notification_service.domain.notification.entities.enums.notification_enums import (
    NotificationStatusEnum,
    NotificationTypeEnum,
)
from notification_service.domain.notification.entities.value_objects.channel_data import ChannelData
from notification_service.domain.notification.exceptions.notification_exceptions import (
    NotificationInvalidRecipientForType,
    NotificationStatusConflict,
)


@dataclass
class Notification:
    uid: UUID
    created_at: datetime
    updated_at: datetime

    type: NotificationTypeEnum
    recipient: str
    subject: str | None
    message: str
    channel_data: ChannelData | None
    status: NotificationStatusEnum
    error_text: str | None

    def __post_init__(self) -> None:
        self._check_recipient_format()

    def _check_recipient_format(self) -> None:
        if self.recipient.startswith("@") and self.type == NotificationTypeEnum.TELEGRAM:
            return
        if self.recipient.startswith("+") and self.type == NotificationTypeEnum.SMS:
            return
        if "@" in self.recipient and not self.recipient.startswith("@") and self.type == NotificationTypeEnum.EMAIL:
            return
        if self.recipient.lstrip("-").isdigit() and self.type == NotificationTypeEnum.TELEGRAM:
            return
        raise NotificationInvalidRecipientForType

    @classmethod
    def create(
        cls,
        notification_type: NotificationTypeEnum,
        recipient: str,
        subject: str | None,
        message: str,
        channel_data: dict | None,
    ) -> "Notification":
        """Фабрика для создания новой сущности."""
        now = datetime.now(UTC)
        channel_data_obj = (
            ChannelData.from_dict(data=channel_data, expected_type=notification_type)
            if channel_data is not None
            else None
        )
        return cls(
            uid=uuid4(),
            created_at=now,
            updated_at=now,
            type=notification_type,
            recipient=recipient,
            subject=subject,
            message=message,
            channel_data=channel_data_obj,
            status=NotificationStatusEnum.QUEUED,
            error_text=None,
        )

    @classmethod
    def reconstitute(
        cls,
        uid: UUID,
        created_at: datetime,
        updated_at: datetime,
        notification_type: NotificationTypeEnum,
        recipient: str,
        subject: str | None,
        message: str,
        channel_data: dict | None,
        status: NotificationStatusEnum,
        error_text: str | None,
    ) -> "Notification":
        """Воссоздает сущность из данных БД."""
        channel_data_obj = (
            ChannelData.from_dict(data=channel_data, expected_type=notification_type)
            if channel_data is not None
            else None
        )
        return cls(
            uid=uid,
            created_at=created_at,
            updated_at=updated_at,
            type=notification_type,
            recipient=recipient,
            subject=subject,
            message=message,
            channel_data=channel_data_obj,
            status=status,
            error_text=error_text,
        )

    def set_pending(self):
        new_status = NotificationStatusEnum.PENDING
        if self.status != NotificationStatusEnum.QUEUED:
            raise NotificationStatusConflict(prev_status=self.status, new_status=new_status)

        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def set_sent(self):
        new_status = NotificationStatusEnum.SENT
        if self.status != NotificationStatusEnum.PENDING:
            raise NotificationStatusConflict(prev_status=self.status, new_status=new_status)

        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def set_failed(self):
        new_status = NotificationStatusEnum.FAILED
        if self.status == new_status:
            raise NotificationStatusConflict(prev_status=self.status, new_status=new_status)

        self.status = new_status
        self.updated_at = datetime.now(UTC)
