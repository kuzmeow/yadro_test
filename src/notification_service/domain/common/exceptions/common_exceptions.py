"""Общие доменные исключения."""

from notification_service.domain.core.domain_exception import DomainException


class CommonException(DomainException):
    """База для всех общих доменных исключений"""


class InternalServerError(CommonException):
    """Internal server error"""

    status_code = 500
    prefix = "SYS"
    service_code = "000"
