from dishka.integrations.flask import FromDishka, inject
from flask import Blueprint, Response, jsonify, request

from notification_service.application.use_cases.notification.enqueue_notification_use_case import (
    EnqueueNotificationUseCase,
)
from notification_service.domain.notification.protocols.notification_db_repo_protocol import NotificationDBProtocol
from notification_service.presentation.routes.notification.notification_mappers import (
    to_enqueue_notification_dto,
    to_read_notification_schema,
    to_search_notification_dto,
)
from notification_service.presentation.routes.notification.notification_schemas import (
    EnqueueNotificationSchema,
    SearchNotificationSchema,
)

notification_bp = Blueprint(name="notifications", import_name=__name__, url_prefix="/api/v1/notifications")


@notification_bp.route("/", methods=["POST"])
@inject
def enqueue_notification(uc: FromDishka[EnqueueNotificationUseCase]) -> tuple[Response, int]:
    """Поставить новое уведомление в очередь на отправку."""
    raw_data = request.get_json(silent=True) or {}
    body = EnqueueNotificationSchema.model_validate(dict(raw_data))
    dto = to_enqueue_notification_dto(schema=body)
    notification = uc.execute(dto)
    return jsonify(to_read_notification_schema(entity=notification).model_dump()), 201


@notification_bp.route("/", methods=["GET"])
@inject
def search(
    notification_db_repo: FromDishka[NotificationDBProtocol],
) -> tuple[Response, int]:
    """Получить отфильтрованный и отсортированный список уведомлений с пагинацией."""
    query = SearchNotificationSchema.model_validate(dict(request.args))
    dto = to_search_notification_dto(schema=query)
    notifications = notification_db_repo.search(dto=dto)
    data = [to_read_notification_schema(entity=n).model_dump() for n in notifications]
    return jsonify(data), 200
