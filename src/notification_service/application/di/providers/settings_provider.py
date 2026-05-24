from dishka import Provider, Scope, provide

from notification_service.application.config import ApplicationSettings
from notification_service.domain.common.entities.value_objects.config import LoggerConfig, PaginationConfig


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    def get_application_settings(self) -> ApplicationSettings:
        return ApplicationSettings()

    @provide
    def get_logger_config(self, settings: ApplicationSettings) -> LoggerConfig:
        return LoggerConfig(
            log_level=settings.LOG_LEVEL,
            pre_registered_loggers=settings.PRE_REGISTERED_LOGGERS,
        )

    @provide
    def get_pagination_config(self, settings: ApplicationSettings) -> PaginationConfig:
        return PaginationConfig(
            default_limit=settings.PAG_DEFAULT_LIMIT,
            default_offset=settings.PAG_DEFAULT_OFFSET,
            max_limit=settings.PAG_MAX_LIMIT,
        )
