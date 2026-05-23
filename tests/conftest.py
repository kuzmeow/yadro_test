"""Конфигурация тестов: testcontainers (локально) / CI services + Dishka + FastAPI."""

import os
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from dishka import Container, Provider, Scope, make_container, provide
from dishka.integrations.flask import FlaskProvider, setup_dishka
from flask import Flask
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from notification_service import LoggerFactory, attach_exception_handlers, register_blueprints
from notification_service.application.config import ApplicationSettings
from notification_service.application.di.providers import InfraProvider, SettingsProvider
from notification_service.infra.db.adapters.postgres_adapter import PostgresAdapter
from notification_service.infra.db.models.base.base_model import Base

# ---------------------------------------------------------------------------
#  Testcontainers / CI services
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def postgres_url():
    """Возвращает URL PostgreSQL.

    В CI (если DATABASE_URL задан) — использует сервис из workflow.
    Локально — поднимает testcontainers.
    """
    if os.environ.get("CI"):
        yield os.environ.get("DATABASE_URL")
    else:
        with PostgresContainer(image="postgres:17.5-alpine", driver="asyncpg") as pg:
            yield pg.get_connection_url()


@pytest.fixture(scope="session")
def redis_url():
    """Возвращает URL Redis.

    В CI (если REDIS_URL задан) — использует сервис из workflow.
    Локально — поднимает testcontainers.
    """
    if os.environ.get("CI"):
        yield os.environ.get("REDIS_URL")
    else:
        with RedisContainer("redis:7-alpine") as rd:
            host = rd.get_container_host_ip()
            port = rd.get_exposed_port(6379)
            yield f"redis://{host}:{port}"


# ---------------------------------------------------------------------------
#  Settings
# ---------------------------------------------------------------------------


class TestSettingsProvider(Provider):
    """Провайдер, подменяющий ApplicationSettings на тестовые."""

    scope = Scope.APP

    def __init__(self, settings: ApplicationSettings):
        super().__init__()
        self._settings = settings

    @provide
    def get_application_settings(self) -> ApplicationSettings:
        return self._settings


@pytest.fixture(scope="session")
def app_settings(postgres_url: str, redis_url: str) -> ApplicationSettings:
    """Создаёт ApplicationSettings поверх testcontainer/CI URL-ов."""
    os.environ["DATABASE_URL"] = postgres_url
    os.environ["REDIS_URL"] = redis_url
    return ApplicationSettings(env="test")


# ---------------------------------------------------------------------------
#  Dishka container
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session")
async def dishka_container(app_settings: ApplicationSettings):
    """Создаёт DI-контейнер Dishka для тестовой сессии."""
    container = make_container(
        FlaskProvider(),
        SettingsProvider(),
        TestSettingsProvider(app_settings),
        InfraProvider(),
    )
    yield container
    container.close()


# ---------------------------------------------------------------------------
#  Database init (auto use для всех интеграционных тестов)
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _init_database(dishka_container: Container):
    """Создаёт таблицы в тестовой БД перед запуском тестов."""
    adapter = dishka_container.get(PostgresAdapter)
    engine = adapter._engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


# ---------------------------------------------------------------------------
#  Flask app + HTTP client
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def test_app(dishka_container: Container) -> Flask:
    """Создаёт Flask приложение с подключённым Dishka."""
    app = Flask("Test Notification Service")
    loger_factory = dishka_container.get(LoggerFactory)
    attach_exception_handlers(app=app, logger_factory=loger_factory)
    register_blueprints(app)
    setup_dishka(dishka_container, app)
    return app


@pytest_asyncio.fixture
async def test_client(test_app) -> AsyncGenerator[AsyncClient, Any]:
    """Возвращает HTTP-клиент для тестирования Flask эндпоинтов."""
    async with AsyncClient(
        base_url="https://test",
        transport=ASGITransport(test_app),
    ) as client:
        yield client


# ---------------------------------------------------------------------------
#  TaskIQ app
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
#  PytestSettings
# ---------------------------------------------------------------------------

pytest_plugins = [
    "tests.common.my_mocker",
    "tests.common.samples.notification_samples",
    "tests.common.factories.adapters",
    "tests.common.factories.repositories",
    "tests.common.factories.services",
]
