from collections.abc import AsyncGenerator
from copy import deepcopy
from dataclasses import asdict
from uuid import uuid4

import pytest
import pytest_asyncio

from notification_service.domain.notification.entities import Notification as DomainNotification
from notification_service.domain.notification.entities.enums.notification_enums import (
    NotificationStatusEnum,
    NotificationTypeEnum,
)
from notification_service.infra.db.models import Notification as NotificationModel


@pytest.fixture
def valid_email_data():
    return {
        "notification_type": NotificationTypeEnum.EMAIL,
        "recipient": "user@example.com",
        "subject": "Welcome",
        "message": "Hello {{name}}!",
        "channel_data": {"reply_to": "support@example.com", "template_id": "welcome_v2"},
    }


@pytest.fixture
def valid_sms_data():
    return {
        "notification_type": NotificationTypeEnum.SMS,
        "recipient": "+79991234567",
        "subject": None,
        "message": "Your code: 1234",
        "channel_data": {"sender_id": "BRAND", "flash": False},
    }


@pytest.fixture
def valid_telegram_data():
    return {
        "notification_type": NotificationTypeEnum.TELEGRAM,
        "recipient": "@username",
        "subject": None,
        "message": "Hi from bot!",
        "channel_data": {"parse_mode": "HTML", "disable_notification": True},
    }


@pytest.fixture
def sample_notification(valid_email_data: dict) -> DomainNotification:
    return DomainNotification.create(
        notification_type=valid_email_data["notification_type"],
        recipient=valid_email_data["recipient"],
        subject=valid_email_data["subject"],
        message=valid_email_data["message"],
        channel_data=valid_email_data["channel_data"],
    )


def domain_notification_to_model(domain_entity: DomainNotification) -> NotificationModel:
    channel_data_dict = asdict(domain_entity.channel_data.value) if domain_entity.channel_data is not None else None
    return NotificationModel(
        uid=domain_entity.uid,
        created_at=domain_entity.created_at,
        updated_at=domain_entity.updated_at,
        type=domain_entity.type,
        recipient=domain_entity.recipient,
        subject=domain_entity.subject,
        message=domain_entity.message,
        channel_data=channel_data_dict,
        status=domain_entity.status,
        error_text=domain_entity.error_text,
    )


@pytest_asyncio.fixture
async def db_sample_notification(
    temporary_db_object, sample_notification: DomainNotification
) -> AsyncGenerator[tuple[DomainNotification, NotificationModel]]:
    domain_entity = deepcopy(sample_notification)
    domain_entity.uid = uuid4()
    model_entity = domain_notification_to_model(domain_entity)
    async with temporary_db_object(model_entity):
        yield domain_entity, model_entity


@pytest_asyncio.fixture
async def db_pending_notification(
    temporary_db_object, sample_notification: DomainNotification
) -> AsyncGenerator[tuple[DomainNotification, NotificationModel]]:
    domain_entity = deepcopy(sample_notification)
    domain_entity.uid = uuid4()
    domain_entity.status = NotificationStatusEnum.PENDING
    model_entity = domain_notification_to_model(domain_entity)
    async with temporary_db_object(model_entity):
        yield domain_entity, model_entity


@pytest_asyncio.fixture
async def db_sent_notification(
    temporary_db_object, sample_notification: DomainNotification
) -> AsyncGenerator[tuple[DomainNotification, NotificationModel]]:
    domain_entity = deepcopy(sample_notification)
    domain_entity.uid = uuid4()
    domain_entity.status = NotificationStatusEnum.SENT
    model_entity = domain_notification_to_model(domain_entity)
    async with temporary_db_object(model_entity):
        yield domain_entity, model_entity
