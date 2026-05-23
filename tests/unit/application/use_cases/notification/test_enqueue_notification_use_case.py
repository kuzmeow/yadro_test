from collections.abc import Callable
from dataclasses import asdict, dataclass

import pytest
from pytest import param
from pytest_mock import MockerFixture

from notification_service.application.use_cases.notification.enqueue_notification_use_case import (
    EnqueueNotificationUseCase,
)
from notification_service.domain.common.protocols.logger_factory_protocol import LoggerFactory
from notification_service.domain.notification.entities import EnqueueNotificationDTO, Notification
from notification_service.domain.notification.protocols import NotificationDBProtocol, NotificationTasksProtocol
from tests.common.factories.adapters import NotificationTasksMockConfig
from tests.common.factories.repositories import NotificationDBMockConfig
from tests.common.my_mocker import SpyFunc

pytestmark = pytest.mark.unit


# --- Fixtures ---


@dataclass(frozen=True)
class ConfigForTest(NotificationDBMockConfig):
    pass


@pytest.fixture
def make_enqueue_notification_uc(
    mocker: MockerFixture,
    make_mock_notification_db: Callable[[NotificationDBMockConfig], NotificationDBProtocol],
    make_mock_notification_tasks: Callable[[NotificationTasksMockConfig], NotificationTasksProtocol],
) -> Callable[[ConfigForTest], EnqueueNotificationUseCase]:
    def _build(cfg: ConfigForTest) -> EnqueueNotificationUseCase:
        mock_notification_db = make_mock_notification_db(NotificationDBMockConfig.from_child(cfg))
        mock_notification_tasks = make_mock_notification_tasks(NotificationTasksMockConfig.from_child(cfg))
        mock_logger_factory = mocker.MagicMock(spec=LoggerFactory)

        uc = EnqueueNotificationUseCase(
            notification_db_repo=mock_notification_db,
            notification_tasks=mock_notification_tasks,
            logger_factory=mock_logger_factory,
        )

        return uc

    return _build


@pytest.fixture
def valid_dto(sample_notification: Notification) -> EnqueueNotificationDTO:
    channel_data_dict = (
        asdict(sample_notification.channel_data.value) if sample_notification.channel_data is not None else None
    )
    return EnqueueNotificationDTO(
        type=sample_notification.type,
        recipient=sample_notification.recipient,
        subject=sample_notification.subject,
        message=sample_notification.message,
        channel_data=channel_data_dict,
    )


# --- Tests ---


# Данный юзкейс не вызывает в конкретно своей бизнес логике никаких исключений
# Поэтому остаётся только протестировать успешный сценарий
# Все ошибки кросс валидации тестируются в юнит тестах доменной сущности
@pytest.mark.parametrize(
    ("dto", "cfg", "result_exception"),
    [
        param("valid", ConfigForTest(), None, id="successful"),
    ],
)
@pytest.mark.asyncio
async def test_enqueue_notification_uc_scenarios(
    dto: str,
    cfg: ConfigForTest,
    result_exception: type[Exception] | None,
    make_enqueue_notification_uc: Callable[[ConfigForTest], EnqueueNotificationUseCase],
    valid_dto: EnqueueNotificationDTO,
    sample_notification: Notification,
):
    """Test EnqueueNotificationUseCase scenarios"""
    uc = make_enqueue_notification_uc(cfg)
    chosen_dto = valid_dto

    if result_exception:
        with pytest.raises(result_exception):
            await uc.execute(chosen_dto)
        return

    result = await uc.execute(chosen_dto)
    assert result == sample_notification


@pytest.mark.asyncio
async def test_enqueue_notification_uc_flow(
    spy: SpyFunc,
    make_enqueue_notification_uc: Callable[[ConfigForTest], EnqueueNotificationUseCase],
    valid_dto: EnqueueNotificationDTO,
):
    """Test successful EnqueueNotificationUseCase flow."""
    uc = make_enqueue_notification_uc(ConfigForTest())

    spy_notification_create = spy(Notification, "create")

    spy_notification_db_save = spy(uc.notification_db_repo, "save")

    spy_notification_tasks_enqueue = spy(uc.notification_tasks, "enqueue_notification")

    await uc.execute(valid_dto)

    spy_notification_create.assert_called_once_with(
        notification_type=valid_dto.type,
        recipient=valid_dto.recipient,
        subject=valid_dto.subject,
        message=valid_dto.message,
        channel_data=valid_dto.channel_data,
    )
    notification: Notification = spy_notification_create.spy_return

    spy_notification_db_save.assert_called_once_with(entity=notification)
    saved = spy_notification_db_save.spy_return

    spy_notification_tasks_enqueue.assert_called_once_with(notification=saved)
