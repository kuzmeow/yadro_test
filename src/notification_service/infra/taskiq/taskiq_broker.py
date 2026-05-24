"""Адаптер TaskIQ, конфигурирующий брокер и хранилище результатов."""

import taskiq
from dishka.integrations.taskiq import setup_dishka
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from notification_service.application.config import ApplicationSettings

settings = ApplicationSettings()

result_backend = RedisAsyncResultBackend(redis_url=settings.REDIS_URL, result_ex_time=3600)

broker = RedisStreamBroker(url=settings.REDIS_URL).with_result_backend(result_backend)


@broker.on_event(taskiq.TaskiqEvents.WORKER_STARTUP)
async def startup(state: taskiq.TaskiqState) -> None:
    """Инициализация DI-контейнера при старте воркера."""
    from notification_service.application.di.container import taskiq_container

    container = taskiq_container()
    setup_dishka(container, broker)

    state.dishka_container = container


@broker.on_event(taskiq.TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: taskiq.TaskiqState) -> None:
    """Очистка ресурсов при остановке воркера."""

    if hasattr(state, "dishka_container"):
        await state.dishka_container.close()
