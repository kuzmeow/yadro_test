import pytest
from pydantic import ValidationError

from notification_service.domain.notification.entities.enums.notification_enums import (
    NotificationStatusEnum,
    NotificationTypeEnum,
)
from notification_service.presentation.routes.notification.notification_schemas import (
    EmailChannelDataSchema,
    EnqueueNotificationSchema,
    SearchNotificationSchema,
    SMSChannelDataSchema,
    TelegramChannelDataSchema,
)


class TestEmailChannelDataSchema:
    def test_valid_full(self):
        EmailChannelDataSchema(
            reply_to="support@example.com",
            cc=["manager@example.com", "audit@example.com"],
            template_id="welcome_v2",
            priority="high",
            from_name="My Service",
        )

    @pytest.mark.parametrize(
        "invalid_email",
        [
            "not-an-email",
            "@example.com",
            "user@",
            "user @example.com",
        ],
    )
    def test_invalid_email_fields_raise(self, invalid_email):
        with pytest.raises(ValidationError, match="value is not a valid email address"):
            EmailChannelDataSchema(reply_to=invalid_email)

    def test_invalid_priority_raises(self):
        with pytest.raises(ValidationError, match="Input should be"):
            EmailChannelDataSchema(priority="urgent")  # type: ignore


class TestTelegramChannelDataSchema:
    def test_valid_full(self):
        TelegramChannelDataSchema(
            parse_mode="HTML",
            disable_notification=True,
            disable_web_page_preview=False,
            reply_to_message_id=12345,
            message_thread_id=789,
        )

    def test_invalid_parse_mode_raises(self):
        with pytest.raises(ValidationError):
            TelegramChannelDataSchema(parse_mode="Markdown")  # type: ignore


class TestSMSChannelDataSchema:
    def test_valid_full(self):
        SMSChannelDataSchema(
            sender_id="MyBrand",
            validity_period=7200,
            encoding="GSM-7",
            flash=True,
            callback_url="https://webhook.example.com/sms/dlr",
        )


class TestRecipientValidation:
    """Тесты сложного Union[EmailStr, TelegramUsername, TelegramChatId, PhoneNumber]."""

    @pytest.mark.parametrize(
        "valid_email",
        [
            "user@example.com",
            "test+tag@sub.domain.co.uk",
            "first.last@company.COM",
        ],
    )
    def test_valid_email_recipient(self, valid_email):
        schema = EnqueueNotificationSchema(type=NotificationTypeEnum.EMAIL, recipient=valid_email, message="Hi")
        assert schema.recipient == valid_email.lower()

    @pytest.mark.parametrize(
        "valid_username",
        [
            "@username",
            "@User_Name123",
            "@" + "a" * 32,
        ],
    )
    def test_valid_telegram_username_recipient(self, valid_username):
        schema = EnqueueNotificationSchema(type=NotificationTypeEnum.TELEGRAM, recipient=valid_username, message="Hi")
        assert schema.recipient == valid_username

    @pytest.mark.parametrize(
        "valid_chat_id",
        [
            "123456789",  # private chat
            "-1001234567890",  # supergroup/channel
            "987654321012345",  # 15 цифр, макс.
        ],
    )
    def test_valid_telegram_chat_id_recipient(self, valid_chat_id):
        schema = EnqueueNotificationSchema(type=NotificationTypeEnum.TELEGRAM, recipient=valid_chat_id, message="Hi")
        assert schema.recipient == valid_chat_id

    @pytest.mark.parametrize(
        "valid_phone",
        [
            "+79991234567",
            "+14155552671",
            "+442071838750",
        ],
    )
    def test_valid_phone_recipient(self, valid_phone):
        schema = EnqueueNotificationSchema(type=NotificationTypeEnum.SMS, recipient=valid_phone, message="Hi")
        assert schema.recipient == valid_phone

    @pytest.mark.parametrize(
        "recipient, error_pattern",
        [
            ("not-an-email", "value is not a valid email address|String should match pattern"),
            ("@us", "String should match pattern"),  # username < 5 символов после @
            ("@user name", "String should match pattern"),  # пробел
            ("+799912", "String should match pattern"),  # телефон < 7 цифр после +
            ("0", "String should match pattern"),  # chat_id не может начинаться с 0
            ("-012345", "String should match pattern"),  # chat_id с ведущим 0 после -
        ],
    )
    def test_invalid_recipient_raises(self, recipient, error_pattern):
        with pytest.raises(ValidationError, match=error_pattern):
            EnqueueNotificationSchema(
                type=NotificationTypeEnum.EMAIL,  # тип не важен
                recipient=recipient,
                message="Hi",
            )


class TestSearchNotificationSchema:
    def test_defaults_are_none(self):
        schema = SearchNotificationSchema()
        assert schema.status is None
        assert schema.limit is None
        assert schema.offset is None

    def test_string_to_enum_coercion(self):
        schema = SearchNotificationSchema(status=NotificationStatusEnum.QUEUED.value)  # type: ignore
        assert schema.status == NotificationStatusEnum.QUEUED

    def test_invalid_status_raises(self):
        with pytest.raises(ValidationError, match="Input should be"):
            SearchNotificationSchema(status="invalid_status")  # type: ignore

    def test_limit_offset_accept_int_strings(self):
        schema = SearchNotificationSchema(limit="20", offset="40")  # type: ignore
        assert schema.limit == 20
        assert schema.offset == 40

    def test_negative_offset_raises(self):
        with pytest.raises(ValidationError, match="Input should be"):
            SearchNotificationSchema(offset=-10)
