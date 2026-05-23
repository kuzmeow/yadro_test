"""Реализация репозитория проектов для PostgreSQL."""

from dataclasses import asdict
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.domain.common.entities.value_objects.config import PaginationConfig
from notification_service.domain.notification.entities.dto.notification_dto import NotificationSearchDTO
from notification_service.domain.notification.entities.notification_entity import Notification as NotificationEntity
from notification_service.domain.notification.exceptions.notification_exceptions import NotificationNotFound
from notification_service.domain.notification.protocols.notification_db_repo_protocol import NotificationDBProtocol
from notification_service.infra.db.mappers.notification.notification_mapper import NotificationMapper
from notification_service.infra.db.models.notification.notification_model import Notification as NotificationModel


class NotificationPgRepository(NotificationDBProtocol):
    """Репозиторий управления уведомлениями в PostgreSQL."""

    def __init__(self, db: AsyncSession, mapper: NotificationMapper, pagination_config: PaginationConfig) -> None:
        """Сохранить адаптер БД и привязать используемые модели.

        :param db: Адаптер PostgreSQL, предоставляющий фабрику сессий.
        :param mapper: Маппер между представлениями сущности.
        """

        self.db = db
        self.model = NotificationModel
        self.mapper = mapper
        self.pagination_config = pagination_config

    async def save(self, entity: NotificationEntity) -> NotificationEntity:
        """Создать запись в хранилище.

        :param entity: Доменная сущность.
        :return: Доменная сущность.
        """

        data = asdict(entity)
        data["channel_data"] = data.pop("channel_data")["value"]
        query = insert(self.model).values(**data).returning(self.model)

        result = await self.db.execute(query)
        await self.db.flush()

        obj = result.scalar_one()

        return self.mapper.orm_to_entity(obj=obj)

    async def update_status(self, entity: NotificationEntity) -> None:
        """Обновляет поле статуса.

        :param entity: Доменная сущность.
        :raises NotificationNotFound: Если объекта с таким uid не существует.
        :return: None
        """

        query = (
            update(self.model)
            .values(status=entity.status)
            .where(self.model.uid == entity.uid)
            .returning(self.model.uid)
        )

        result = await self.db.execute(query)
        updated_uid = result.scalar_one_or_none()

        if updated_uid is None:
            raise NotificationNotFound

        await self.db.flush()

    async def delete(self, uid: UUID) -> None:
        """Удалить запись из хранилища.

        :param uid: Идентификатор.
        :raises NotificationNotFound: Если объекта с таким uid не существует.
        :return: None
        """
        query = delete(self.model).where(self.model.uid == uid).returning(self.model.uid)
        result = await self.db.execute(query)

        deleted_uid = result.scalar_one_or_none()

        if deleted_uid is None:
            raise NotificationNotFound()

        await self.db.flush()

    async def get_by_uid(self, uid: UUID) -> NotificationEntity | None:
        """Получить данные проекта по идентификатору.

        :param uid: Идентификатор.
        :return: Доменная сущность или None, если запись не найдена.
        """

        query = select(self.model).where(self.model.uid == uid)
        result = await self.db.execute(query)
        obj = result.scalar_one_or_none()

        if obj is None:
            return obj

        return self.mapper.orm_to_entity(obj=obj)

    async def search(self, dto: NotificationSearchDTO) -> list[NotificationEntity]:
        """Поиск данных по фильтрам с пагинацией.

        :param dto: Данные для поиска и пагинации.
        :return: Список доменных сущностей.
        """
        query = select(self.model)

        if dto.status is not None:
            query = query.where(self.model.status == dto.status)

        query = query.order_by(self.model.created_at.desc())

        limit = dto.limit if dto.limit is not None else self.pagination_config.default_limit
        offset = dto.offset if dto.offset is not None else self.pagination_config.default_offset

        limit = min(limit, self.pagination_config.max_limit)

        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        objs = result.scalars().all()

        return [self.mapper.orm_to_entity(obj=obj) for obj in objs]
