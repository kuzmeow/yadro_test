"""Экспорт основных моделей базы данных приложения."""

from notification_service.infra.db.models.base.base_model import Base
from notification_service.infra.db.models.notification.notification_model import Notification

__all__ = ["Base", "Notification"]
