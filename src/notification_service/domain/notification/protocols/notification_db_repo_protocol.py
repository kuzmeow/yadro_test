"""Протокол доступа к данным уведомлений в хранилище."""

import uuid
from typing import Protocol

from notification_service.domain.notification.entities.dto.notification_dto import SearchNotificationDTO
from notification_service.domain.notification.entities.notification_entity import Notification


class NotificationDBProtocol(Protocol):
    """Протокол репозитория уведомлений."""

    async def save(self, entity: Notification) -> Notification:
        """Создать запись в хранилище.

        :param entity: Доменная сущность.
        :return: Доменная сущность.
        """

    async def update_status(self, entity: Notification) -> None:
        """Обновляет поля статусов пользователя.

        :param entity: Доменная сущность.
        :return: None
        """

    async def delete(self, uid: uuid.UUID) -> None:
        """Удалить запись из хранилища.

        :param uid: Идентификатор.
        :return: None
        """

    async def get_by_uid(self, uid: uuid.UUID) -> Notification | None:
        """Получить данные проекта по идентификатору.

        :param uid: Идентификатор.
        :return: Доменная сущность или None, если запись не найдена.
        """

    async def search(self, dto: SearchNotificationDTO) -> list[Notification]:
        """Поиск данных по фильтрам с пагинацией.

        :param dto: Данные для поиска и пагинации.
        :return: Список доменных сущностей.
        """
