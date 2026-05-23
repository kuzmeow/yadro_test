"""Конфигурация DI-контейнера Dishka."""

from dishka import AsyncContainer, Container, make_async_container, make_container
from dishka.integrations.flask import FlaskProvider

from notification_service.application.di.providers import (
    InfraProvider,
    SettingsProvider,
)
from notification_service.application.di.providers.notification_provider import NotificationProvider


def create_container() -> Container:
    """Создать и настроить синхронный DI-контейнер."""
    return make_container(
        FlaskProvider(),
        SettingsProvider(),
        InfraProvider(),
        NotificationProvider(),
    )


def create_async_container() -> AsyncContainer:
    """Создать и настроить асинхронный DI-контейнер."""
    return make_async_container(
        FlaskProvider(),
        SettingsProvider(),
        InfraProvider(),
        NotificationProvider(),
    )
