from notification_service.domain.core.domain_exception import DomainException
from notification_service.domain.notification.entities.enums.notification_enums import (
    NotificationStatusEnum,
    NotificationTypeEnum,
)


class NotificationException(DomainException):
    """База для всех исключений, связанных с уведомлениями."""

    prefix = "NTF"


class NotificationNotFound(NotificationException):
    """Notification not found"""

    status_code = 404
    service_code = "001"


class NotificationInvalidRecipientForType(NotificationException):
    """Recipient format is invalid for provided type"""

    status_code = 400
    service_code = "002"


class NotificationInvalidChannelDataForType(NotificationException):
    """Channel Data format is invalid for provided type"""

    status_code = 400
    service_code = "003"

    def __init__(self, expected_type: NotificationTypeEnum, invalid_keys: set[str]):
        super().__init__(details={"expected_type": expected_type, "invalid_keys": invalid_keys})


class NotificationStatusConflict(NotificationException):
    """Notification status conflict"""

    status_code = 409
    service_code = "004"

    def __init__(self, prev_status: NotificationStatusEnum, new_status: NotificationStatusEnum):
        reason = f"Cannot set {prev_status} notification status to {new_status}"
        super().__init__(details={"reason": reason})
