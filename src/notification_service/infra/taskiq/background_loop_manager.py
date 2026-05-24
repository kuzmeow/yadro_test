import asyncio
import threading
from collections.abc import Coroutine
from typing import Any

from notification_service.domain.common.protocols.logger_factory_protocol import LoggerFactory


class BackgroundLoopManager:
    """Менеджер постоянного асинхронного loop для выполнения задач из sync-контекста."""

    def __init__(self, logger_factory: LoggerFactory) -> None:
        self.logger = logger_factory(__name__)
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._loop is not None and not self._loop.is_closed():
            return

        self._loop = asyncio.new_event_loop()

        def _run_loop() -> None:
            asyncio.set_event_loop(self._loop)
            assert self._loop is not None
            self._loop.run_forever()

        self._thread = threading.Thread(target=_run_loop, daemon=True, name="bg-async-loop")
        assert self._thread is not None
        self._thread.start()

    def schedule(self, coro: Coroutine[Any, Any, None]) -> None:
        """Планирует корутину на фоновый loop (thread-safe)."""
        if self._loop is None or self._loop.is_closed():
            self.start()

        assert self._loop is not None
        asyncio.run_coroutine_threadsafe(coro, self._loop)

        # def _log_exc(fut):
        #     fut.result()
        #
        # future.add_done_callback(_log_exc)
