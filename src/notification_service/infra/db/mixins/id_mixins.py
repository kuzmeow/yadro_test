"""Миксин для добавления UUID-первичного ключа в модель."""

import uuid

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UIDMixin:
    """Добавляет поле `uid` с типом UUID и автогенерацией значения."""

    uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
