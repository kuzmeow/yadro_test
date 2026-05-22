from dataclasses import dataclass, field

from notification_service.domain.common.entities.enums.config_enums import LoggerLevel


@dataclass(frozen=True)
class LoggerConfig:
    log_level: LoggerLevel = LoggerLevel.INFO
    max_size_mb: int = 10
    backup_count: int = 5
    pre_registered_loggers: list[str] = field(default_factory=lambda: ["uvicorn", "dishka"])
