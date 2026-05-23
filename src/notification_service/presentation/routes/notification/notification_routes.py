from dishka.integrations.flask import FromDishka
from flask import Blueprint, Response, jsonify

from notification_service.application.use_cases.notification.enqueue_notification_use_case import (
    EnqueueNotificationUseCase,
)
from notification_service.domain.notification.protocols.notification_db_repo_protocol import NotificationDBProtocol
from notification_service.presentation.core.router_validators import validate_body, validate_query
from notification_service.presentation.routes.notification.notification_mappers import (
    to_enqueue_notification_dto,
    to_read_notification_schema,
    to_search_notification_dto,
)
from notification_service.presentation.routes.notification.notification_schemas import (
    EnqueueNotificationSchema,
    SearchNotificationSchema,
)

project_blueprint = Blueprint(name="notifications", import_name=__name__, url_prefix="/notifications")


@project_blueprint.route("/", methods=["POST"])
@validate_body(EnqueueNotificationSchema)
async def enqueue_notification(
    body: EnqueueNotificationSchema, uc: FromDishka[EnqueueNotificationUseCase]
) -> tuple[Response, int]:
    """Поставить новое уведомление в очередь на отправку."""
    dto = to_enqueue_notification_dto(schema=body)
    notification = await uc.execute(dto)
    return jsonify(to_read_notification_schema(entity=notification).model_dump()), 201


@project_blueprint.route("/", methods=["GET"])
@validate_query(SearchNotificationSchema)
async def search(
    query: SearchNotificationSchema,
    notification_db_repo: FromDishka[NotificationDBProtocol],
) -> tuple[Response, int]:
    """Получить отфильтрованный и отсортированный список уведомлений с пагинацией."""
    dto = to_search_notification_dto(schema=query)
    notifications = await notification_db_repo.search(dto=dto)
    data = [to_read_notification_schema(entity=n).model_dump() for n in notifications]
    return jsonify(data), 200
