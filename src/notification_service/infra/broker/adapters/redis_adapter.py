"""Адаптер подключения к Redis для брокера сообщений."""

from collections.abc import Generator
from contextlib import contextmanager

from redis import ConnectionPool, Redis

from notification_service.application.config import ApplicationSettings


class RedisAdapter:
    """Создает и переиспользует пул соединений Redis."""

    def __init__(self, settings: ApplicationSettings) -> None:
        """Проинициализировать пул соединений на основе настроек."""
        self._url = settings.REDIS_URL
        self.settings = settings
        self._pool: ConnectionPool = self._init_pool()

    def _init_pool(self) -> ConnectionPool:
        """Создать пул подключений Redis с заданными параметрами."""
        return ConnectionPool.from_url(
            self._url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=self.settings.REDIS_MAX_CONNECTIONS,
        )

    @contextmanager
    def get_client(self) -> Generator[Redis]:
        """Получить клиент Redis из пула в виде синхронного контекстного менеджера."""
        redis_client = Redis(connection_pool=self._pool)
        try:
            yield redis_client
        finally:
            redis_client.close()
