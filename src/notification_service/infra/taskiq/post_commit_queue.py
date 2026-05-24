from collections.abc import Coroutine
from typing import Any

from notification_service.domain.common.protocols.logger_factory_protocol import LoggerFactory
from notification_service.infra.taskiq.background_loop_manager import BackgroundLoopManager


class PostCommitQueue:
    """Очередь корутин, которые планируются на фоновый loop после commit()."""

    def __init__(self, logger_factory: LoggerFactory, loop_manager: BackgroundLoopManager) -> None:
        self.logger = logger_factory(__name__)
        self.loop_manager = loop_manager
        self._coroutines: list[Coroutine[Any, Any, Any]] = []

    def schedule(self, coro: Coroutine[Any, Any, Any]) -> None:
        """Добавить корутину в очередь."""
        self._coroutines.append(coro)

    def execute_all(self) -> None:
        """Планирует все корутины на фоновый loop (вызывается после commit)."""
        if not self._coroutines:
            return

        coros = self._coroutines.copy()
        self._coroutines.clear()

        for coro in coros:
            self.loop_manager.schedule(coro)
