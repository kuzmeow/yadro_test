from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from notification_service.domain.notification.entities.enums.notification_enums import (
    NotificationStatusEnum,
    NotificationTypeEnum,
)
from notification_service.domain.notification.entities.notification_entity import Notification
from notification_service.domain.notification.entities.value_objects.channel_data import ChannelData, EmailChannelData
from notification_service.domain.notification.exceptions.notification_exceptions import (
    NotificationInvalidChannelDataForType,
    NotificationInvalidRecipientForType,
    NotificationStatusConflict,
)


class TestNotificationCreate:
    def test_create_sets_queued_status_and_auto_fields(self, valid_email_data):
        notif = Notification.create(**valid_email_data)

        assert isinstance(notif.uid, UUID)
        assert notif.created_at.tzinfo == UTC
        assert notif.updated_at.tzinfo == UTC
        assert notif.status == NotificationStatusEnum.QUEUED
        assert notif.error_text is None

    def test_create_converts_channel_data_to_value_object(self, valid_email_data):
        notif = Notification.create(**valid_email_data)

        assert isinstance(notif.channel_data, ChannelData)
        assert isinstance(notif.channel_data.value, EmailChannelData)
        assert notif.channel_data.value.reply_to == "support@example.com"
        assert notif.channel_data.value.template_id == "welcome_v2"

    def test_create_with_none_channel_data(self, valid_email_data):
        valid_email_data["channel_data"] = None
        notif = Notification.create(**valid_email_data)

        assert notif.channel_data is None

    @pytest.mark.parametrize(
        "recipient",
        [
            "not-an-email",  # нет @
            "@username",  # Telegram-формат для email
            "+79991234567",  # телефон для email
            "12345",  # chat_id для email
        ],
    )
    def test_create_invalid_recipient_for_email_raises(self, recipient):
        with pytest.raises(NotificationInvalidRecipientForType):
            Notification.create(
                notification_type=NotificationTypeEnum.EMAIL,
                recipient=recipient,
                subject=None,
                message="Hi",
                channel_data=None,
            )

    @pytest.mark.parametrize(
        "recipient",
        [
            "89991234567",  # нет +
            "user@domain",  # email для sms
            "@username",  # telegram для sms
        ],
    )
    def test_create_invalid_recipient_for_sms_raises(self, recipient):
        with pytest.raises(NotificationInvalidRecipientForType):
            Notification.create(
                notification_type=NotificationTypeEnum.SMS,
                recipient=recipient,
                subject=None,
                message="Code",
                channel_data=None,
            )

    @pytest.mark.parametrize(
        "recipient",
        [
            "username",  # нет @
            "+79991234567",  # телефон для telegram
            "user@example.com",  # email для telegram
        ],
    )
    def test_create_invalid_recipient_for_telegram_raises(self, recipient):
        with pytest.raises(NotificationInvalidRecipientForType):
            Notification.create(
                notification_type=NotificationTypeEnum.TELEGRAM,
                recipient=recipient,
                subject=None,
                message="Hi",
                channel_data=None,
            )

    @pytest.mark.parametrize(
        "recipient, expected_type",
        [
            ("@User_Name", NotificationTypeEnum.TELEGRAM),  # username
            ("-1001234567890", NotificationTypeEnum.TELEGRAM),  # group chat_id
            ("123456789", NotificationTypeEnum.TELEGRAM),  # private chat_id
            ("+14155552671", NotificationTypeEnum.SMS),  # US phone
            ("test@sub.domain.co.uk", NotificationTypeEnum.EMAIL),  # complex email
        ],
    )
    def test_create_valid_recipients_pass(self, recipient, expected_type):
        notif = Notification.create(
            notification_type=expected_type,
            recipient=recipient,
            subject=None,
            message="Test",
            channel_data=None,
        )
        assert notif.recipient == recipient


class TestNotificationReconstitute:
    def test_reconstitute_preserves_all_fields(self, valid_email_data):
        uid = uuid4()
        created = datetime.now(UTC) - timedelta(hours=1)
        updated = datetime.now(UTC)

        notif = Notification.reconstitute(
            uid=uid,
            created_at=created,
            updated_at=updated,
            notification_type=valid_email_data["notification_type"],
            recipient=valid_email_data["recipient"],
            subject=valid_email_data["subject"],
            message=valid_email_data["message"],
            channel_data=valid_email_data["channel_data"],
            status=NotificationStatusEnum.SENT,
            error_text=None,
        )

        assert notif.uid == uid
        assert notif.created_at == created
        assert notif.updated_at == updated
        assert notif.status == NotificationStatusEnum.SENT
        assert isinstance(notif.channel_data, ChannelData)

    def test_reconstitute_with_none_channel_data(self, valid_email_data):
        notif = Notification.reconstitute(
            uid=uuid4(),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            notification_type=valid_email_data["notification_type"],
            recipient=valid_email_data["recipient"],
            subject=valid_email_data["subject"],
            message=valid_email_data["message"],
            channel_data=None,
            status=NotificationStatusEnum.FAILED,
            error_text="Timeout",
        )

        assert notif.channel_data is None
        assert notif.error_text == "Timeout"


class TestNotificationStatusTransitions:
    def test_queued_to_pending_to_sent(self, valid_email_data):
        notif = Notification.create(**valid_email_data)

        notif.set_pending()
        assert notif.status == NotificationStatusEnum.PENDING

        notif.set_sent()
        assert notif.status == NotificationStatusEnum.SENT

    def test_queued_to_sent_raises(self, valid_email_data):
        notif = Notification.create(**valid_email_data)

        with pytest.raises(NotificationStatusConflict) as exc:
            notif.set_sent()

        details = exc.value.details
        assert details is not None
        assert isinstance(details, dict)
        reason = details["reason"]
        assert NotificationStatusEnum.QUEUED.value in reason
        assert NotificationStatusEnum.SENT.value in reason

    def test_sent_to_pending_raises(self, valid_email_data):
        notif = Notification.create(**valid_email_data)
        notif.set_pending()
        notif.set_sent()

        with pytest.raises(NotificationStatusConflict):
            notif.set_pending()

    @pytest.mark.parametrize(
        "initial_status",
        [
            NotificationStatusEnum.QUEUED,
            NotificationStatusEnum.PENDING,
            NotificationStatusEnum.SENT,
        ],
    )
    def test_can_fail_from_any_status(self, valid_email_data, initial_status):
        notif = Notification.create(**valid_email_data)
        notif.status = initial_status

        notif.set_failed()
        assert notif.status == NotificationStatusEnum.FAILED

    def test_failed_to_failed_raises(self, valid_email_data):
        notif = Notification.create(**valid_email_data)
        notif.set_failed()

        with pytest.raises(NotificationStatusConflict):
            notif.set_failed()

    def test_updated_at_changes_on_status_transition(self, valid_email_data):
        notif = Notification.create(**valid_email_data)
        notif.updated_at = datetime.now(UTC) - timedelta(seconds=10)
        old_updated = notif.updated_at

        notif.set_pending()
        assert notif.updated_at > old_updated


class TestNotificationEdgeCases:
    def test_channel_data_validation_happens_in_create(self):
        with pytest.raises(NotificationInvalidChannelDataForType):
            Notification.create(
                notification_type=NotificationTypeEnum.EMAIL,
                recipient="test@example.com",
                subject=None,
                message="Hi",
                channel_data={"sender_id": "BRAND"},  # ключ от SMS
            )
