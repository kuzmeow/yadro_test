"""SQLAlchemy-модель уведомления."""

from sqlalchemy import TEXT, VARCHAR, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from notification_service.domain.notification.entities.enums.notification_enums import (
    NotificationStatusEnum,
    NotificationTypeEnum,
)
from notification_service.infra.db.mixins.id_mixins import UIDMixin
from notification_service.infra.db.mixins.timestamp_mixins import TimestampsMixin
from notification_service.infra.db.models.base.base_model import Base


class Notification(UIDMixin, TimestampsMixin, Base):
    type: Mapped[NotificationTypeEnum] = mapped_column(Enum(NotificationTypeEnum), nullable=False)
    recipient: Mapped[str] = mapped_column(VARCHAR(320), nullable=False)
    subject: Mapped[str | None] = mapped_column(VARCHAR(500), nullable=True)
    message: Mapped[str] = mapped_column(TEXT, nullable=False)
    channel_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[NotificationStatusEnum] = mapped_column(Enum(NotificationStatusEnum), nullable=False)
    error_text: Mapped[str | None] = mapped_column(VARCHAR(500), nullable=True)
