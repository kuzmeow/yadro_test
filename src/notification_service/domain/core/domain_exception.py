"""Базовое доменное исключение приложения."""


class DomainException(Exception):
    """Общее исключение для бизнес-ошибок доменного слоя."""

    status_code: int = 500
    prefix: str = "SYS"
    service_code: str = "000"

    def __init__(self, message: str | None = None, details: dict | list[dict] | None = None):
        self.message = message or self.__doc__ or "Internal Server Error"
        self.details = details
        super().__init__(self.message)

    @property
    def code(self) -> str:
        return f"{self.prefix}-{self.service_code}"

    def to_dict(self) -> dict:
        payload: dict = {"code": self.code, "message": self.message, "details": self.details or {}}
        return {"error": payload}
