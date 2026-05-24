from dataclasses import dataclass

from notification_service.domain.common.entities.enums.config_enums import LoggerLevel


@dataclass(frozen=True)
class LoggerConfig:
    log_level: LoggerLevel
    pre_registered_loggers: list[str]


@dataclass(frozen=True)
class PaginationConfig:
    default_limit: int
    default_offset: int
    max_limit: int
