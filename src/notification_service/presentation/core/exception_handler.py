from flask import Flask, Response, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import NotFound

from notification_service.domain.common.exceptions.common_exceptions import InternalServerError
from notification_service.domain.common.protocols.logger_factory_protocol import LoggerFactory
from notification_service.domain.core.domain_exception import DomainException


def attach_exception_handlers(app: Flask, logger_factory: LoggerFactory):
    """Зарегистрировать глобальные обработчики на экземпляре Flask."""
    logger = logger_factory(name=__name__)

    def make_error_response(code: str, message: str, details: dict, status_code: int) -> tuple:
        return jsonify({"error": {"code": code, "message": message, "details": details}}), status_code

    @app.errorhandler(DomainException)
    async def domain_exception_handler(exc: DomainException) -> tuple[Response, int]:
        """Все доменные исключения -> структурированный JSON"""
        if isinstance(exc, InternalServerError):
            logger.error("InternalServerError", extra={"details": exc.details})
            exc.details = {}

        return jsonify(exc.to_dict()), exc.status_code

    @app.errorhandler(ValidationError)
    def pydantic_validation_handler(exc: ValidationError) -> tuple[Response, int]:
        """Ошибки валидации Pydantic -> VAL-001"""
        fields = []
        for error in exc.errors():
            loc = ".".join(str(x) for x in error["loc"] if x != "body")
            fields.append({"field": loc, "reason": error["msg"]})

        return make_error_response(
            code="VAL-001", message="Validation failed", details={"fields": fields}, status_code=422
        )

    @app.errorhandler(NotFound)
    def api_not_found_handler(exc: NotFound) -> tuple:
        """Обработчик 404: ресурс не найден."""

        return make_error_response(
            code="SYS-001",
            message="Resource not found",
            details={"path": exc.description if hasattr(exc, "description") else None},
            status_code=404,
        )

    @app.errorhandler(Exception)
    def generic_exception_handler(exc: Exception) -> tuple[Response, int]:
        """Все необработанные исключения -> SYS-000"""
        logger.exception(f"Unhandled {type(exc).__name__}", extra={"error_class": type(exc).__name__})
        return make_error_response(code="SYS-000", message="Internal Server Error", details={}, status_code=500)
