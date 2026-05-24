"""Создание и запуск приложения."""

import uvicorn
from asgiref.wsgi import WsgiToAsgi
from dishka.integrations.flask import setup_dishka
from flask import Flask
from flask_cors import CORS

from notification_service.application.config import ApplicationSettings
from notification_service.application.di.container import flask_container
from notification_service.domain.common.protocols.logger_factory_protocol import LoggerFactory
from notification_service.presentation.core.exception_handler import attach_exception_handlers
from notification_service.presentation.routes import register_blueprints


def run_app() -> None:
    """Инициализировать Flask и запустить сервер Uvicorn.

    :return: None
    """

    # Какой кошмар
    # Почему не FastApi?
    app = Flask("Notification Service")

    register_blueprints(app)

    container = flask_container()
    setup_dishka(container, app)

    settings = container.get(ApplicationSettings)
    logger_factory = container.get(LoggerFactory)
    logger = logger_factory(name=__name__)

    attach_exception_handlers(app=app, logger_factory=logger_factory)

    CORS(
        app,
        origins=settings.CORS_ALLOW_ORIGINS,
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    logger.info("Starting application...")
    asgi_app = WsgiToAsgi(app)
    uvicorn.run(
        asgi_app,
        host="0.0.0.0",
        port=8000,
        loop=settings.ASYNCIO_LOOP,
        log_config=None,
    )
