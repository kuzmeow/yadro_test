import pytest

from notification_service.domain.notification.entities.enums.notification_enums import NotificationTypeEnum
from notification_service.domain.notification.entities.value_objects.channel_data import (
    ChannelData,
    EmailChannelData,
    SMSChannelData,
    TelegramChannelData,
)
from notification_service.domain.notification.exceptions.notification_exceptions import (
    NotificationInvalidChannelDataForType,
)


class TestChannelDataFactory:
    """Тесты фабричного метода ChannelData.from_dict."""

    @pytest.mark.parametrize(
        "raw_data, expected_type, expected_cls, expected_attrs",
        [
            (
                {"reply_to": "support@example.com"},
                NotificationTypeEnum.EMAIL,
                EmailChannelData,
                {"reply_to": "support@example.com"},
            ),
            (
                {"parse_mode": "HTML", "disable_notification": True},
                NotificationTypeEnum.TELEGRAM,
                TelegramChannelData,
                {"parse_mode": "HTML", "disable_notification": True},
            ),
            (
                {"sender_id": "BRAND", "validity_period": 3600, "flash": False},
                NotificationTypeEnum.SMS,
                SMSChannelData,
                {"sender_id": "BRAND", "validity_period": 3600, "flash": False},
            ),
            ({}, NotificationTypeEnum.EMAIL, EmailChannelData, {"priority": None, "from_name": None}),
        ],
    )
    def test_valid_data_creates_correct_instance(self, raw_data, expected_type, expected_cls, expected_attrs):
        result = ChannelData.from_dict(raw_data, expected_type)

        assert isinstance(result, ChannelData)
        assert isinstance(result.value, expected_cls)

        for attr, value in expected_attrs.items():
            assert getattr(result.value, attr) == value

    @pytest.mark.parametrize(
        "raw_data, expected_type",
        [
            ({"sender_id": "BRAND"}, NotificationTypeEnum.EMAIL),
            ({"reply_to": "a@b.com"}, NotificationTypeEnum.SMS),
            ({"parse_mode": "HTML", "flash": True}, NotificationTypeEnum.TELEGRAM),
            ({"unknown_field": 123}, NotificationTypeEnum.EMAIL),
            ({"reply_to": "a@b.com", "sender_id": "APP"}, NotificationTypeEnum.EMAIL),
        ],
    )
    def test_invalid_keys_raises_domain_exception(self, raw_data, expected_type):
        with pytest.raises(NotificationInvalidChannelDataForType) as exc_info:
            ChannelData.from_dict(raw_data, expected_type)

        details = exc_info.value.details
        assert details is not None
        assert isinstance(details, dict)
        assert details["expected_type"] == expected_type
        assert len(details["invalid_keys"]) > 0

    def test_none_values_are_preserved(self):
        data = {"reply_to": None, "cc": None, "template_id": "tpl_1"}
        result = ChannelData.from_dict(data, NotificationTypeEnum.EMAIL)

        value = result.value
        assert isinstance(value, EmailChannelData)
        assert value.reply_to is None
        assert value.cc is None
        assert value.template_id == "tpl_1"

    def test_immutable_value_object(self):
        result = ChannelData.from_dict({"sender_id": "APP"}, NotificationTypeEnum.SMS)

        assert isinstance(result.value, SMSChannelData)

        with pytest.raises((TypeError, AttributeError)):
            result.value.sender_id = "HACKED"  # type: ignore
