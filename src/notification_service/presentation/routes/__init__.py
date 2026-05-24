"""Инициализация корневого роутера."""

from flask import Flask

from notification_service.presentation.routes.notification.notification_routes import notification_bp


def register_blueprints(app: Flask):
    """Инициализация и регистрация всех роутеров."""
    app.register_blueprint(notification_bp)
