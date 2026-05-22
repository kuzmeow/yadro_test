"""Конфигурация проектного логгера с ротацией файлов."""

import logging

from notification_service.domain.common.entities.value_objects.config import LoggerConfig


class ProjectLogger:
    """Создает и настраивает логгеры с консольным и файловым выводом."""

    def __init__(self, settings: LoggerConfig):
        """Прочитать настройки и подготовить инфраструктуру логирования.

        :param settings: Доменная конфигурация с параметрами логирования.
        """

        self.log_level = settings.log_level
        self.max_log_size = settings.max_size_mb
        self.backup_count = settings.backup_count
        self.pre_registered_loggers = settings.pre_registered_loggers

        self._console_handler = self._create_console_handler()

        for logger_name in self.pre_registered_loggers:
            self.get_logger(logger_name)

    def _create_console_handler(self) -> logging.Handler:
        """Создать обработчик вывода логов в консоль."""

        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(self.get_log_formatter())
        return console_handler

    @staticmethod
    def get_log_formatter() -> logging.Formatter:
        """Создать общий форматтер логов проекта."""

        return logging.Formatter(
            fmt="[%(asctime)-25s][%(levelname)-8s][%(name)-35s]"
            "[%(filename)-20s][%(funcName)-25s][%(lineno)-5d][%(message)s]"
        )

    def get_logger(self, name: str | None = None) -> logging.Logger:
        """Вернуть логгер с подключенными обработчиками проекта.

        :param name: Имя логгера; если None, используется корневой.
        :return: Настроенный экземпляр `Logger`.
        """

        logger = logging.getLogger(name)

        if not logger.hasHandlers():
            logger.setLevel(self.log_level)

            logger.addHandler(self._console_handler)

            if name is not None:
                logger.propagate = False

        return logger
