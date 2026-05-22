"""Полный конфиг приложения."""

from typing import Literal

from dynaconf import Dynaconf, Validator


class ApplicationSettings(Dynaconf):
    DATABASE_URL: str
    REDIS_URL: str
    CORS_ALLOW_ORIGINS: list[str]
    SECURE_COOKIES: bool
    SECURE_SAMESITE: Literal["lax", "none"]

    def __init__(self, **kwargs):
        validators = [
            Validator("DATABASE_URL", must_exist=True),
            Validator("REDIS_URL", must_exist=True),
            Validator(
                "CORS_ALLOW_ORIGINS",
                default=["http://localhost:3000"],
            ),
            Validator("SECURE_COOKIES", cast=bool, default=True),
            Validator("SECURE_SAMESITE", default="lax"),
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
