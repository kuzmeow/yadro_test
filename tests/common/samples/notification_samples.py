import pytest

from notification_service.domain.notification.entities.enums.notification_enums import NotificationTypeEnum


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
