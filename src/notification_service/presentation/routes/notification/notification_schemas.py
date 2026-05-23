from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, StringConstraints

from notification_service.domain.notification.entities.enums.notification_enums import (
    NotificationStatusEnum,
    NotificationTypeEnum,
)


class EmailChannelDataSchema(BaseModel):
    reply_to: EmailStr | None = None
    cc: list[EmailStr] | None = None
    template_id: str | None = None
    priority: Literal["low", "normal", "high"] | None = None
    from_name: str | None = None


class TelegramChannelDataSchema(BaseModel):
    parse_mode: Literal["HTML", "MarkdownV2"] | None = None
    disable_notification: bool | None = None
    disable_web_page_preview: bool | None = None
    reply_to_message_id: int | None = None
    message_thread_id: int | None = None


class SMSChannelDataSchema(BaseModel):
    sender_id: str | None = None
    validity_period: int | None = None
    encoding: Literal["GSM-7", "UCS-2", "auto"] | None = None
    flash: bool | None = None
    callback_url: str | None = None


TelegramUsername = Annotated[str, StringConstraints(pattern=r"^@[a-zA-Z0-9_]{5,32}$")]
TelegramChatId = Annotated[str, StringConstraints(pattern=r"^-?[1-9]\d{4,15}$")]
PhoneNumber = Annotated[str, StringConstraints(pattern=r"^\+[1-9]\d{6,14}$")]

Recipient = Annotated[
    PhoneNumber | TelegramUsername | EmailStr | TelegramChatId,
    StringConstraints(min_length=1, max_length=320, strip_whitespace=True),
]
Subject = Annotated[str, StringConstraints(min_length=1, max_length=500, strip_whitespace=True)]
Message = Annotated[str, StringConstraints(min_length=1, max_length=2000, strip_whitespace=True)]
ChannelData = EmailChannelDataSchema | TelegramChannelDataSchema | SMSChannelDataSchema


class EnqueueNotificationSchema(BaseModel):
    """Входные данные для регистрации уведомления.

    :param type: Тип канала.
    :param recipient: Получатель.
    :param subject: Тема.
    :param message: Текст сообщения.
    :param channel_data: Параметры канала.
    """

    type: NotificationTypeEnum
    recipient: Recipient
    subject: Subject | None = None
    message: Message
    channel_data: ChannelData | None = None


class SearchNotificationSchema(BaseModel):
    """Входные данные для поиска уведомлений.

    :param status: Фильтр статуса.
    :param limit: Ограничение на количество возвращаемых уведомлений.
    :param offset: Смещение от начала отфильтрованного и отсортированного списка.
    """

    status: NotificationStatusEnum | None = None
    limit: int | None = Field(default=None, ge=0)
    offset: int | None = Field(default=None, ge=0)


class ReadNotificationSchema(BaseModel):
    """Ответ API с данными уведомления

    :param uid: Уникальный идентификатор.
    :param status: Статус уведомления.
    :param error: Текст ошибки.
    """

    uid: UUID
    status: NotificationStatusEnum
    error: str | None
