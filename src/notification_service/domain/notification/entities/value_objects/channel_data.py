from dataclasses import dataclass
from typing import ClassVar

from notification_service.domain.notification.entities.enums.notification_enums import NotificationTypeEnum
from notification_service.domain.notification.exceptions.notification_exceptions import (
    NotificationInvalidChannelDataForType,
)


@dataclass(frozen=True)
class EmailChannelData:
    ALLOWED_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "reply_to",
            "cc",
            "template_id",
            "priority",
            "from_name",
        }
    )

    reply_to: str | None = None
    cc: list[str] | None = None
    template_id: str | None = None
    priority: str | None = None
    from_name: str | None = None


@dataclass(frozen=True)
class TelegramChannelData:
    ALLOWED_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "parse_mode",
            "disable_notification",
            "disable_web_page_preview",
            "reply_to_message_id",
            "message_thread_id",
        }
    )

    parse_mode: str | None = None
    disable_notification: bool | None = None
    disable_web_page_preview: bool | None = None
    reply_to_message_id: int | None = None
    message_thread_id: int | None = None


@dataclass(frozen=True)
class SMSChannelData:
    ALLOWED_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "sender_id",
            "validity_period",
            "encoding",
            "flash",
            "callback_url",
        }
    )

    sender_id: str | None = None
    validity_period: int | None = None
    encoding: str | None = None
    flash: bool | None = None
    callback_url: str | None = None


GenericChannelData = EmailChannelData | TelegramChannelData | SMSChannelData


@dataclass(frozen=True)
class ChannelData:
    value: GenericChannelData

    _TYPE_MAPPING: ClassVar[dict[NotificationTypeEnum, type[GenericChannelData]]] = {
        NotificationTypeEnum.EMAIL: EmailChannelData,
        NotificationTypeEnum.TELEGRAM: TelegramChannelData,
        NotificationTypeEnum.SMS: SMSChannelData,
    }

    @classmethod
    def from_dict(cls, data: dict, expected_type: NotificationTypeEnum) -> "ChannelData":
        target_cls = cls._TYPE_MAPPING[expected_type]
        allowed_keys = target_cls.ALLOWED_KEYS
        data_keys = set(data.keys())

        if not data_keys.issubset(allowed_keys):
            invalid_keys = data_keys - allowed_keys
            raise NotificationInvalidChannelDataForType(expected_type=expected_type, invalid_keys=invalid_keys)

        return cls(value=target_cls(**data))
