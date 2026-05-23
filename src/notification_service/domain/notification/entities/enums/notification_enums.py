from enum import StrEnum


class NotificationTypeEnum(StrEnum):
    EMAIL = "email"
    TELEGRAM = "telegram"
    SMS = "sms"


class NotificationStatusEnum(StrEnum):
    QUEUED = "queued"
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
