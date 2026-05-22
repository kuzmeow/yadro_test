"""Полный конфиг приложения."""

from typing import Literal

from dynaconf import Dynaconf, Validator

from notification_service.domain.common.entities.enums.config_enums import LoggerLevel


class ApplicationSettings(Dynaconf):
    ASYNCIO_LOOP: str
    DATABASE_URL: str
    REDIS_URL: str
    CORS_ALLOW_ORIGINS: list[str]
    SECURE_COOKIES: bool
    SECURE_SAMESITE: Literal["lax", "none"]
    LOG_LEVEL: LoggerLevel
    PRE_REGISTERED_LOGGERS: list[str]

    def __init__(self, **kwargs):
        validators = [
            Validator("SECURE_SAMESITE", default="asyncio"),
            Validator("DATABASE_URL", must_exist=True),
            Validator("REDIS_URL", must_exist=True),
            Validator(
                "CORS_ALLOW_ORIGINS",
                default=["http://localhost:3000"],
            ),
            Validator("SECURE_COOKIES", cast=bool, default=True),
            Validator("SECURE_SAMESITE", default="lax"),
            Validator("LOG_LEVEL", cast=LoggerLevel, default=LoggerLevel.INFO),
            Validator("PRE_REGISTERED_LOGGERS", cast=list[str], default=["uvicorn", "dishka"]),
        ]

        defaults = {
            "settings_files": ["config/settings.yaml"],
            "envvar_prefix": False,
            "environments": True,
            "load_dotenv": True,
            "validators": validators,
        }
        defaults.update(kwargs)

        super().__init__(**defaults)
