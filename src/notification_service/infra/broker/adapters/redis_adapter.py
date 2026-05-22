"""Адаптер подключения к Redis для брокера сообщений."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from redis.asyncio import ConnectionPool, Redis

from notification_service.application.config import ApplicationSettings


class RedisAdapter:
    """Создает и переиспользует пул соединений Redis."""

    def __init__(self, settings: ApplicationSettings) -> None:
        """Проинициализировать пул соединений на основе настроек."""

        self._url = settings.REDIS_URL
        self.settings = settings
        self._pool: ConnectionPool = self._init_pool()

    def _init_pool(self) -> ConnectionPool:
        """Создать пул подключений Redis с заданными параметрами.

        :return: Готовый пул соединений.
        """

        return ConnectionPool.from_url(
            self._url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=self.settings.REDIS_MAX_CONNECTIONS,
        )

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[Redis]:
        """Получить клиент Redis из пула в виде асинхронного контекстного менеджера.

        :yield: Асинхронный клиент Redis.
        """

        redis_client = Redis(connection_pool=self._pool)
        try:
            yield redis_client
        finally:
            await redis_client.aclose()
