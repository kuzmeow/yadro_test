from collections.abc import Callable
from dataclasses import dataclass

import pytest
from pytest_mock import MockerFixture

from notification_service.domain.notification.protocols import NotificationTasksProtocol
from tests.common.factories.mock_config import MockConfig


@dataclass(frozen=True)
class NotificationTasksMockConfig(MockConfig):
    pass


@pytest.fixture
def make_mock_notification_tasks(
    mocker: "MockerFixture",
) -> Callable[[NotificationTasksMockConfig], NotificationTasksProtocol]:
    def _build(cfg: NotificationTasksMockConfig) -> NotificationTasksProtocol:
        adapter = mocker.MagicMock(spec=NotificationTasksProtocol)

        adapter.enqueue_notification = mocker.AsyncMock()

        return adapter

    return _build
