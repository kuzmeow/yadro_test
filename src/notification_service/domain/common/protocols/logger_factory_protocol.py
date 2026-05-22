import logging
from typing import Protocol


class LoggerFactory(Protocol):
    """Протокол для фабрики логгеров."""

    def __call__(self, name: str | None = None) -> logging.Logger: ...
