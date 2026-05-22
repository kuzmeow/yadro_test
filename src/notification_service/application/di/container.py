"""Конфигурация DI-контейнера Dishka."""

from dishka import make_async_container
from dishka.integrations.flask import FlaskProvider

from notification_service.application.di.providers import (
    InfraProvider,
    SettingsProvider,
)


def create_container():
    """Создать и настроить асинхронный DI-контейнер."""
    return make_async_container(
        FlaskProvider(),
        SettingsProvider(),
        InfraProvider(),
    )
