from collections.abc import Callable
from dataclasses import dataclass

import pytest
from pytest_mock import MockerFixture

from notification_service.domain.notification.entities import Notification
from notification_service.domain.notification.exceptions import NotificationNotFound
from notification_service.domain.notification.protocols import NotificationDBProtocol
from tests.common.factories.mock_config import MockConfig


@dataclass(frozen=True)
class NotificationDBMockConfig(MockConfig):
    update_status_raise: bool = False


@pytest.fixture
def make_mock_notification_db(
    mocker: MockerFixture, sample_notification: Notification
) -> Callable[[NotificationDBMockConfig], NotificationDBProtocol]:
    def _build(cfg: NotificationDBMockConfig) -> NotificationDBProtocol:
        repo = mocker.MagicMock(spec=NotificationDBProtocol)

        repo.save = mocker.AsyncMock()
        repo.save.return_value = sample_notification

        repo.update_status = mocker.AsyncMock()
        if cfg.update_status_raise:
            repo.update_status.side_effect = NotificationNotFound

        repo.search = mocker.AsyncMock()
        repo.search.return_value = [sample_notification]

        return repo

    return _build
