from collections.abc import Callable
from dataclasses import dataclass

import pytest
from pytest_mock import MockerFixture

from notification_service.domain.notification.exceptions import NotificationSendingFailed
from notification_service.domain.notification.protocols import NotificationServiceProtocol
from tests.common.factories.mock_config import MockConfig


@dataclass(frozen=True)
class NotificationServiceMockConfig(MockConfig):
    send_notification_raise: bool = False


@pytest.fixture
def make_mock_password_service(
    mocker: MockerFixture,
) -> Callable[[NotificationServiceMockConfig], NotificationServiceProtocol]:
    def _build(cfg: NotificationServiceMockConfig) -> NotificationServiceProtocol:
        service = mocker.MagicMock(spec=NotificationServiceProtocol)

        service.send_notification = mocker.AsyncMock()
        if cfg.send_notification_raise:
            service.send_notification.side_effect = NotificationSendingFailed

        return service

    return _build
