from dataclasses import asdict

import pytest_asyncio
from dishka import Container
from sqlalchemy.orm import Session

from notification_service.domain.common.entities.value_objects.config import PaginationConfig
from notification_service.domain.notification.entities import Notification as DomainNotification
from notification_service.domain.notification.entities import NotificationStatusEnum, SearchNotificationDTO
from notification_service.infra.db.mappers.notification.notification_mapper import NotificationMapper
from notification_service.infra.db.models import Notification as NotificationModel
from notification_service.infra.db.repositories.notification.notification_db_repository import NotificationPgRepository


@pytest_asyncio.fixture
async def test_notification_pg_repository(db_session: Session, dishka_container: Container) -> NotificationPgRepository:
    """Возвращает тестируемый экземпляр репозитория NotificationPgRepository"""

    return NotificationPgRepository(
        db=db_session,
        mapper=dishka_container.get(NotificationMapper),
        pagination_config=dishka_container.get(PaginationConfig),
    )


async def test_create_notification_successfully(
    clear_notification_db_table_after_test,
    db_session: Session,
    test_notification_pg_repository: NotificationPgRepository,
    sample_notification: DomainNotification,
):
    obj_from_db = db_session.get(NotificationModel, sample_notification.uid)
    assert obj_from_db is None

    result = test_notification_pg_repository.save(sample_notification)
    assert result == sample_notification

    obj_from_db = db_session.get(NotificationModel, result.uid)

    channel_data_dict = (
        asdict(sample_notification.channel_data.value) if sample_notification.channel_data is not None else None
    )
    assert obj_from_db is not None
    assert obj_from_db.uid == sample_notification.uid
    assert obj_from_db.created_at == sample_notification.created_at
    assert obj_from_db.updated_at == sample_notification.updated_at
    assert obj_from_db.type == sample_notification.type
    assert obj_from_db.recipient == sample_notification.recipient
    assert obj_from_db.subject == sample_notification.subject
    assert obj_from_db.message == sample_notification.message
    assert obj_from_db.channel_data == channel_data_dict
    assert obj_from_db.status == sample_notification.status
    assert obj_from_db.error_text == sample_notification.error_text


async def test_update_notification_status_successfully(
    clear_notification_db_table_after_test,
    db_sample_notification: tuple[DomainNotification, NotificationModel],
    db_session: Session,
    test_notification_pg_repository: NotificationPgRepository,
):
    domain_entity, _ = db_sample_notification
    domain_entity.set_pending()
    test_notification_pg_repository.update_status(entity=domain_entity)

    obj_from_db = db_session.get(NotificationModel, domain_entity.uid)
    assert obj_from_db is not None
    assert obj_from_db.status == domain_entity.status


async def test_update_notification_status_to_failed_successfully(
    clear_notification_db_table_after_test,
    db_sample_notification: tuple[DomainNotification, NotificationModel],
    db_session: Session,
    test_notification_pg_repository: NotificationPgRepository,
):
    domain_entity, _ = db_sample_notification
    domain_entity.set_failed()
    domain_entity.error_text = "Failed for some reason"
    test_notification_pg_repository.update_status(entity=domain_entity)

    obj_from_db = db_session.get(NotificationModel, domain_entity.uid)
    assert obj_from_db is not None
    assert obj_from_db.status == domain_entity.status
    assert obj_from_db.error_text == domain_entity.error_text


async def test_search_notifications_without_params_successfully(
    clear_notification_db_table_after_test,
    db_pending_notification: tuple[DomainNotification, NotificationModel],
    db_sent_notification: tuple[DomainNotification, NotificationModel],
    test_notification_pg_repository: NotificationPgRepository,
):
    pending_domain_entity, _ = db_pending_notification
    sent_domain_entity, _ = db_sent_notification

    dto = SearchNotificationDTO(status=None, limit=None, offset=None)
    result = test_notification_pg_repository.search(dto=dto)
    assert pending_domain_entity in result
    assert sent_domain_entity in result


async def test_search_notifications_with_status_successfully(
    clear_notification_db_table_after_test,
    db_pending_notification: tuple[DomainNotification, NotificationModel],
    db_sent_notification: tuple[DomainNotification, NotificationModel],
    test_notification_pg_repository: NotificationPgRepository,
):
    pending_domain_entity, _ = db_pending_notification
    sent_domain_entity, _ = db_sent_notification

    dto = SearchNotificationDTO(status=NotificationStatusEnum.PENDING, limit=None, offset=None)
    result = test_notification_pg_repository.search(dto=dto)
    assert pending_domain_entity in result
    assert sent_domain_entity not in result


async def test_search_notifications_with_limit_successfully(
    clear_notification_db_table_after_test,
    db_pending_notification: tuple[DomainNotification, NotificationModel],
    db_sent_notification: tuple[DomainNotification, NotificationModel],
    test_notification_pg_repository: NotificationPgRepository,
):
    dto = SearchNotificationDTO(status=None, limit=1, offset=None)
    result = test_notification_pg_repository.search(dto=dto)
    assert len(result) == 1
