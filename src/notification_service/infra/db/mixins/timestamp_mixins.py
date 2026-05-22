"""Миксины временных меток для SQLAlchemy-моделей."""

import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class CreatedAtMixin:
    """Добавляет поле `created_at` с автоматическим временем создания."""

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class UpdatedAtMixin:
    """Добавляет поле `updated_at` с автоматическим обновлением."""

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class TimestampsMixin(CreatedAtMixin, UpdatedAtMixin):
    """Комбинирует поля `created_at` и `updated_at` в одной модели."""
